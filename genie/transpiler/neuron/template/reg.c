// This file will contain functions related to xxx_reg

void _{{ filename }}_reg() {
  // common
  int _vectorized = 1;
  _initlists();
{{ ion_reg }}
{{ ion_symbol }}
  // common
  register_mech(_mechanism,
                nrn_alloc,
                nrn_cur,
                nrn_jacob,
                nrn_state,
                nrn_init,
                hoc_nrnpointerindex,
                2);

  _extcall_thread = (Datum*)ecalloc(1, sizeof(Datum));
  _thread_mem_init(_extcall_thread);
  _thread1data_inuse = 0;

  // common
  _mechtype = nrn_get_mechtype(_mechanism[1]);
  _nrn_setdata_reg(_mechtype, _setdata);

  _nrn_thread_reg(_mechtype, 1, _thread_mem_init);
  _nrn_thread_reg(_mechtype, 0, _thread_cleanup);
  _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
  _nrn_thread_table_reg(_mechtype, _check_table_thread);
  hoc_register_dparam_size(_mechtype, {{ hoc_dparam_size }});

  // common
  hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
  hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
  hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
  ivoc_help("help ?1 hh_k /volume1/home/hp120263/k00634/neuron_kplus/specials/sparc64/hh_k.mod\n");
  hoc_register_limits(_mechtype, _hoc_parm_limits);
  hoc_register_units(_mechtype, _hoc_parm_units);
}

static void _initlists(){
  double _x;
  double* _p = &_x;
  int _i;
  static int _first = 1;
  if (!_first) {
    return;
  }
{{ initlists }}
  _first = 0;
}

static void _thread_mem_init(Datum* _thread) {
  if (_thread1data_inuse) {
    _thread[_gth]._pval = (double*)ecalloc(6, sizeof(double));
  } else {
    _thread[_gth]._pval = _thread1data;
    _thread1data_inuse = 1;
  }
}

static void _thread_cleanup(Datum* _thread) {
  if (_thread[_gth]._pval == _thread1data) {
    _thread1data_inuse = 0;
  } else {
    free((void*)_thread[_gth]._pval);
  }
}
static void _update_ion_pointer(Datum* _ppvar) {
{{ nrn_update_ion_pointer }}
}

static void _check_table_thread(double* _p,
                                Datum* _ppvar,
                                Datum* _thread,
                                _NrnThread* _nt,
                                int _type) {
  _check_rates(_p, _ppvar, _thread, _nt);
}
