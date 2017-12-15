static int _ode_count(int _type){
  return {{ num_states }};
}

static void _ode_map(int _ieq,
                     double** _pv,
                     double** _pvdot,
                     double* _pp,
                     Datum* _ppd,
                     double* _atol,
                     int _type) {
  double* _p;
  Datum* _ppvar;
  int _i;
  _p = _pp;
  _ppvar = _ppd;
 	_cvode_ieq = _ieq;
 	for (_i=0; _i < {{ num_states }}; ++_i) {
 	  _pv[_i] = _pp + _slist1[_i];
    _pvdot[_i] = _pp + _dlist1[_i];
 		_cvode_abstol(_atollist, _atol, _i);
 	}
}

static void _ode_spec(_NrnThread* _nt, _Memb_list* _ml, int _type) {
  double* _p;
  Datum* _ppvar;
  Datum* _thread;
  Node* _nd;
  double _v;
  int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml];
    _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
{{ read_ions }}
    _ode_spec1(_p, _ppvar, _thread, _nt);
  }
}

static int _ode_spec1(double* _p,
    Datum* _ppvar,
    Datum* _thread,
    _NrnThread* _nt) {
  int _reset = 0;
  rates(_threadargscomma_ v);
{{ ode_spec1 }}
  return _reset;
}

static void _ode_matsol(_NrnThread* _nt, _Memb_list* _ml, int _type) {
  double* _p;
  Datum* _ppvar;
  Datum* _thread;
  Node* _nd;
  double _v;
  int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml];
    _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
{{ read_ions }}
    _ode_matsol1(_p, _ppvar, _thread, _nt);
  }
}

static int _ode_matsol1(double* _p,
    Datum* _ppvar,
    Datum* _thread,
    _NrnThread* _nt) {
  rates (_threadargscomma_ v);
{{ ode_matsol1 }}
  return 0;
}
