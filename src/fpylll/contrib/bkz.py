# -*- coding: utf-8 -*-
"""
Block Korkine Zolotarev algorithm in Python.

..  moduleauthor:: Martin R.  Albrecht <martinralbrecht+fpylll@googlemail.com>

This module reimplements fplll's BKZ algorithm in Python.  It has feature parity with the C++
implementation in fplll's core.  Additionally, this implementation collects some additional
statistics.  Hence, it should provide a good basis for implementing variants of this algorithm.
"""
from __future__ import absolute_import
import time
from fpylll import IntegerMatrix, GSO, LLL
from fpylll import BKZ
from fpylll import Enumeration as Enum
from fpylll import EnumerationError
from .bkz_stats import BKZStats


class BKZReduction:
    """
    An implementation of the BKZ algorithm in Python.

    This class has feature parity with the C++ implementation in fplll's core.  Additionally, this
    implementation collects some additional statistics.  Hence, it should provide a good basis for
    implementing variants of this algorithm.
    """
    def __init__(self, A):
        """Construct a new instance of the BKZ algorithm.

        :param A: an integer matrix

        """
        if not isinstance(A, IntegerMatrix):
            raise TypeError("Matrix must be IntegerMatrix but got type '%s'"%type(A))

        # run LLL first
        wrapper = LLL.Wrapper(A)
        wrapper()

        self.A = A
        self.M = GSO.Mat(A, flags=GSO.ROW_EXPO)
        self.lll_obj = LLL.Reduction(self.M)

    def __call__(self, params):
        """Run the BKZ algorithm with parameters `param`.

        :param params: BKZ parameters

        """
        stats = BKZStats(self, verbose=params.flags & BKZ.VERBOSE)

        if params.flags & BKZ.AUTO_ABORT:
            auto_abort = BKZ.AutoAbort(self.M, self.A.nrows)

        cputime_start = time.clock()

        self.M.discover_all_rows()

        i = 0
        while True:
            with stats.context("tour"):
                clean = self.tour(params, 0, self.A.nrows, stats)
            if clean or params.block_size >= self.A.nrows:
                break
            if (params.flags & BKZ.AUTO_ABORT) and auto_abort.test_abort():
                break
            if (params.flags & BKZ.MAX_LOOPS) and i >= params.max_loops:
                break
            if (params.flags & BKZ.MAX_TIME) and time.clock() - cputime_start >= params.max_time:
                break
            i += 1

        stats.finalize()
        self.stats = stats

    def tour(self, params, min_row, max_row, stats=None):
        """One BKZ loop over all indices.

        :param params: BKZ parameters
        :param min_row: start index ≥ 0
        :param max_row: last index ≤ n

        :returns: ``True`` if no change was made and ``False`` otherwise
        """
        clean = True
        for kappa in range(min_row, max_row-1):
            block_size = min(params.block_size, max_row - kappa)
            clean &= self.svp_reduction(kappa, params, block_size, stats)
            if stats:
                stats.log_clean_kappa(kappa, clean)
        return clean

    def svp_preprocessing(self, kappa, params, block_size, stats):
        """Perform preprocessing for calling the SVP oracle

        :param kappa: current index
        :param params: BKZ parameters
        :param block_size: block size
        :param stats: object for maintaining statistics

        :returns: ``True`` if no change was made and ``False`` otherwise

        .. note::

            ``block_size`` may be smaller than ``params.block_size`` for the last blocks.

        """
        clean = True

        self.lll_obj(0, kappa, kappa + block_size)
        if self.lll_obj.nswaps > 0:
            clean = False

        if params.preprocessing:
            preproc = params.preprocessing
            auto_abort = BKZ.AutoAbort(self.M, kappa + block_size, kappa)
            cputime_start = time.clock()

            i = 0
            while True:
                clean_inner = self.tour(preproc, kappa, kappa + block_size)
                if clean_inner:
                    break
                else:
                    clean = clean_inner
                if auto_abort.test_abort():
                    break
                if (preproc.flags & BKZ.MAX_LOOPS) and i >= preproc.max_loops:
                    break
                if (preproc.flags & BKZ.MAX_TIME) and time.clock() - cputime_start >= preproc.max_time:
                    break
                i += 1

        return clean

    def svp_call(self, kappa, params, block_size, stats=None):
        """Call SVP oracle

        :param kappa: current index
        :param params: BKZ parameters
        :param block_size: block size
        :param stats: object for maintaining statistics

        :returns: Coordinates of SVP solution or ``None`` if none was found.

        ..  note::

            ``block_size`` may be smaller than ``params.block_size`` for the last blocks.
        """
        max_dist, expo = self.M.get_r_exp(kappa, kappa)
        delta_max_dist = self.lll_obj.delta * max_dist

        if params.flags & BKZ.GH_BND:
            max_dist, expo = self.M.compute_gaussian_heuristic_distance(kappa, block_size,
                                                                        max_dist, expo, params.gh_factor)
        try:
            solution, max_dist = Enum.enumerate(self.M, max_dist, expo,
                                                kappa, kappa + block_size,
                                                params.pruning)
        except EnumerationError as msg:
            if params.flags & BKZ.GH_BND:
                return None
            else:
                raise EnumerationError(msg)

        if max_dist >= delta_max_dist:
            return None
        else:
            return solution

    def svp_postprocessing(self, solution, kappa, params, block_size, stats=None):
        """Insert SVP solution into basis and LLL reduce.

        :param solution: coordinates of an SVP solution
        :param kappa: current index
        :param params: BKZ parameters
        :param block_size: block size
        :param stats: object for maintaining statistics

        :returns: ``True`` if no change was made and ``False`` otherwise
        """
        if solution is None:
            return True

        nonzero_vectors = len([x for x in solution if x])
        if nonzero_vectors == 1:
            first_nonzero_vector = None
            for i in range(block_size):
                if abs(solution[i]) == 1:
                    first_nonzero_vector = i
                    break

            self.M.move_row(kappa + first_nonzero_vector, kappa)
            self.lll_obj.size_reduction(kappa, kappa + 1)

        else:
            d = self.M.d
            self.M.create_row()

            with self.M.row_ops(d, d+1):
                for i in range(block_size):
                    self.M.row_addmul(d, kappa + i, solution[i])

            self.M.move_row(d, kappa)
            self.lll_obj(kappa, kappa, kappa + block_size + 1)
            self.M.move_row(kappa + block_size, d)

            self.M.remove_last_row()

        return False

    def svp_reduction(self, kappa, params, block_size, stats=None):
        """Find shortest vector in projected lattice of dimension ``block_size`` and insert into
        current basis.

        :param kappa: current index
        :param params: BKZ parameters
        :param block_size: block size
        :param stats: object for maintaining statistics

        :returns: ``True`` if no change was made and ``False`` otherwise
        """
        if stats is None:
            stats = BKZStats(self)

        clean = True
        with stats.context("preproc"):
            clean_pre = self.svp_preprocessing(kappa, params, block_size, stats)
        clean &= clean_pre

        with stats.context("svp"):
            solution = self.svp_call(kappa, params, block_size, stats)

        with stats.context("postproc"):
            clean_post = self.svp_postprocessing(solution, kappa, params, block_size, stats)
        clean &= clean_post

        return clean
