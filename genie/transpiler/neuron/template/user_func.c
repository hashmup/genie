/* connect user functions to hoc names */
static VoidFunc hoc_intfunc[] = {
  "setdata_{{ filename }}", _hoc_setdata,
  "rates_{{ filename }}", _hoc_rates,
  "vtrap_{{ filename }}", _hoc_vtrap,
  0, 0
};

static void _hoc_setdata() {
  Prop *_prop, *hoc_getdata_range(int);
  _prop = hoc_getdata_range(_mechtype);
  _setdata(_prop);
  hoc_retpushx(1.);
}

static void _setdata(Prop* _prop) {
  _extcall_prop = _prop;
}

static void _hoc_rates(void) {
  double _r;
  double* _p;
  Datum* _ppvar;
  Datum* _thread;
  _NrnThread* _nt;
  if (_extcall_prop) {
    _p = _extcall_prop->param;
    _ppvar = _extcall_prop->dparam;
  } else {
    _p = (double*)0;
    _ppvar = (Datum*)0;
  }
  _thread = _extcall_thread;
  _nt = nrn_threads;

  _check_rates(_p, _ppvar, _thread, _nt);
  _r = 1.;
  rates( _p, _ppvar, _thread, _nt, *getarg(1));
  hoc_retpushx(_r);
}

static void _check_rates(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  static int _maktable=1;
  int _i, _j, _ix = 0;
  double _xi, _tmax;
  static double _sav_celsius;
  if (!usetable) {
    return;
  }
  if (_sav_celsius != celsius) {
    _maktable = 1;
  }
  if (_maktable) {
    double _x, _dx;
    _maktable=0;
    _tmin_rates =  - 100.0;
    _tmax =  100.0;
    _dx = (_tmax - _tmin_rates)/200.;
    _mfac_rates = 1./_dx;
    for (_i=0, _x=_tmin_rates; _i < 201; _x += _dx, _i++) {
      _f_rates(_p, _ppvar, _thread, _nt, _x);
      _t_minf[_i] = minf;
      _t_mtau[_i] = mtau;
      _t_hinf[_i] = hinf;
      _t_htau[_i] = htau;
      _t_ninf[_i] = ninf;
      _t_ntau[_i] = ntau;
    }
    _sav_celsius = celsius;
  }
}

static int rates(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _lv) {
  _n_rates(_p, _ppvar, _thread, _nt, _lv);
  return 0;
}

static void _n_rates(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _lv) {
  int _i, _j;
  double _xi, _theta;
  if (!usetable) {
    _f_rates(_p, _ppvar, _thread, _nt, _lv);
    return;
  }
  _xi = _mfac_rates * (_lv - _tmin_rates);
  _i = (int) _xi;
  if (_xi <= 0.) {
    minf = _t_minf[0];
    mtau = _t_mtau[0];
    hinf = _t_hinf[0];
    htau = _t_htau[0];
    ninf = _t_ninf[0];
    ntau = _t_ntau[0];
    return;
  }
  if (_i >= 200) {
    minf = _t_minf[200];
    mtau = _t_mtau[200];
    hinf = _t_hinf[200];
    htau = _t_htau[200];
    ninf = _t_ninf[200];
    ntau = _t_ntau[200];
    return;
  }
  _theta = _xi - (double)_i;
  minf = _t_minf[_i] + _theta*(_t_minf[_i+1] - _t_minf[_i]);
  mtau = _t_mtau[_i] + _theta*(_t_mtau[_i+1] - _t_mtau[_i]);
  hinf = _t_hinf[_i] + _theta*(_t_hinf[_i+1] - _t_hinf[_i]);
  htau = _t_htau[_i] + _theta*(_t_htau[_i+1] - _t_htau[_i]);
  ninf = _t_ninf[_i] + _theta*(_t_ninf[_i+1] - _t_ninf[_i]);
  ntau = _t_ntau[_i] + _theta*(_t_ntau[_i+1] - _t_ntau[_i]);
}


static int  _f_rates ( _threadargsprotocomma_ double _lv ) {
  double _lalpha , _lbeta , _lsum , _lq10;
  _lq10 = pow(3.0 , ((celsius - 6.3 ) / 10.0));
  _lalpha = .1 * vtrap(_threadargscomma_ - (_lv + 40.0), 10.0);
  _lbeta = 4.0 * exp(- (_lv + 65.0) / 18.0);
  _lsum = _lalpha + _lbeta;
  mtau = 1.0 / (_lq10 * _lsum);
  minf = _lalpha / _lsum;
  _lalpha = .07 * exp (- (_lv + 65.0) / 20.0);
  _lbeta = 1.0 / (exp(- (_lv + 35.0) / 10.0) + 1.0);
  _lsum = _lalpha + _lbeta;
  htau = 1.0 / (_lq10 * _lsum);
  hinf = _lalpha / _lsum;
  _lalpha = .01 * vtrap(_threadargscomma_ - (_lv + 55.0), 10.0);
  _lbeta = .125 * exp(- (_lv + 65.0) / 80.0);
  _lsum = _lalpha + _lbeta;
  ntau = 1.0 / (_lq10 * _lsum);
  ninf = _lalpha / _lsum;
  return 0;
}

static void _hoc_vtrap(void) {
  double _r;
  double* _p;
  Datum* _ppvar;
  Datum* _thread;
  _NrnThread* _nt;
  if (_extcall_prop) {
    _p = _extcall_prop->param;
    _ppvar = _extcall_prop->dparam;
  } else {
    _p = (double*)0;
    _ppvar = (Datum*)0;
  }
  _thread = _extcall_thread;
  _nt = nrn_threads;
  _r =  vtrap (_p, _ppvar, _thread, _nt, *getarg(1), *getarg(2));
  hoc_retpushx(_r);
}

double vtrap (_threadargsprotocomma_ double _lx , double _ly) {
  double _lvtrap;
  if (fabs(_lx / _ly) < 1e-6) {
    _lvtrap = _ly * (1.0 - _lx / _ly / 2.0);
  } else {
    _lvtrap = _lx / (exp(_lx / _ly ) - 1.0);
  }
  return _lvtrap;
}
