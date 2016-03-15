# -*- coding: utf-8 -*-

from gso cimport MatGSO
from fpylll cimport lll_reduction_core, fplll_type_t

cdef class LLLReduction:

    cdef fplll_type_t _type
    cdef lll_reduction_core _core

    cdef readonly MatGSO M
    cdef double _delta
    cdef double _eta
