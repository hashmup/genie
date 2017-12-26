static void nrn_alloc(Prop* _prop) {
  Prop *prop_ion;
  double *_p;
  Datum *_ppvar;
  _p = nrn_prop_data_alloc(_mechtype, {{ nrn_alloc.param_size }}, _prop);
  /*initialize range parameters*/
{{ nrn_alloc.init_range_parameter }}
  _prop->param = _p;
  _prop->param_size = {{ nrn_alloc.param_size }};
  _ppvar = nrn_prop_datum_alloc(_mechtype, {{ nrn_alloc.num_prop_ion }}, _prop);
  _prop->dparam = _ppvar;
  /*connect ionic variables to this model*/
{{ nrn_alloc.connect_ionic_variables }}
}

static void nrn_init(_NrnThread* _nt, _Memb_list* _ml, int _type) {
  double* _p;
  Datum* _ppvar;
  Datum* _thread;
  Node *_nd;
  double _v;
  int* _ni;
  int _iml, _cntml;
  /* check condition for kplus*/
#ifndef CACHEVEC
#error
  printf("KPLSU ERROR : CASHEVEC must be enabled\n");
  exit(-1);
#endif
  if(!use_cachevec) {
    printf("KPLSU ERROR : use_cachevec must be enabled\n");
    exit(-1);
  }
  if(!usetable) {
    printf("KPLSU ERROR : usetable must be enabled\n");
    exit(-1);
  }

  _ni = _ml->_nodeindices;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;

  // initialize m,h,n
{{ nrn_init.link_table }}
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml];
    _ppvar = _ml->_pdata[_iml];

    _v = VEC_V(_ni[_iml]);
    v = _v;
{{ nrn_init.read_ions }}

    initmodel(_p, _ppvar, _thread, _nt);

    // initialize m,h,n
{{ nrn_init.initialize_table }}
  }

{{ nrn_init.restruct_table}}
}

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  rates(_threadargscomma_ v);
{{ nrn_init.initmodel }}
}

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type) {
  Datum* _thread;
  int* _ni;
  int _iml, _cntml;
  double local_dt = dt;

  double _theta_table[BUFFER_SIZE];
  int _i_table[BUFFER_SIZE];

  static double local_mfac_rates;
  static double local_tmin_rates;

{{ nrn_state.link_table }}

  _ni = _ml->_nodeindices;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;

  if(_cntml > BUFFER_SIZE){
    printf("KPLSU ERROR : Compartment size (%d) is larger Buffer (%d)\n", _cntml, BUFFER_SIZE);
    exit(-1);
  }

  local_mfac_rates = _mfac_rates;
  local_tmin_rates = _tmin_rates;


  double *vec_v = _nt->_actual_v;

#ifdef KPLUS_USE_MOD_OMP
#pragma omp parallel
#endif
  {

#ifdef KPLUS_USE_MOD_OMP
#pragma omp for
#endif
#pragma loop noalias
#pragma loop norecurrence
  for (_iml = 0; _iml < _cntml; _iml++){
    double _v = vec_v[_ni[_iml]];
    _i_table[_iml] = (int)(_v - local_tmin_rates);
    _theta_table[_iml] = (_v - local_tmin_rates) - (FLOAT)_i_table[_iml];
  }

#ifdef KPLUS_USE_MOD_OMP
#pragma omp for
#endif
#pragma loop noalias
#pragma loop norecurrence
  for (_iml = 0; _iml < _cntml; _iml++){
    if(!( _i_table[_iml] >= 200 || _i_table[_iml] < 0.0)) {
      ;
    } else if(_i_table[_iml] >= 200) {
      _theta_table[_iml] = 1.0;
      _i_table[_iml] = 199;
    } else if(_i_table[_iml] < 0.0) {
      _theta_table[_iml] = 0.0;
      _i_table[_iml] = 0;
    }
  }

{{ nrn_state.calc_table }}
  }
}

static void nrn_cur(_NrnThread* _nt, _Memb_list* _ml, int _type)
{
  Datum* _thread;
  Node *_nd;
  int* _ni;
  int _iml, _cntml;


#ifdef KPLUS_USE_FAPP_RANGE
  fapp_start("nrn_cur", 31, 4);
#endif

  _ni = _ml->_nodeindices;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
{{ nrn_cur.link_table }}

  const double *vec_v = _nt->_actual_v;
  double *vec_rhs = _nt->_actual_rhs;
{{ nrn_cur.break_point_without_current }}
#else
{{ nrn_cur.break_point }}
#endif

#ifdef KPLUS_USE_FAPP_RANGE
  fapp_stop("nrn_cur", 31, 4);
#endif
}

static void nrn_jacob(_NrnThread* _nt, _Memb_list* _ml, int _type) {
  Datum* _thread;
  int* _ni;
  int _iml, _cntml;

  _ni = _ml->_nodeindices;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;

  double *vec_d = _nt->_actual_d;
  double *g_table = &(_g_table[BUFFER_SIZE * _nt->_id]);

#ifdef KPLUS_USE_MOD_OMP
#pragma omp parallel for
#endif
  for (_iml = 0; _iml < _cntml; ++_iml) {
    vec_d[_ni[_iml]] += g_table[_iml];
  }
}
