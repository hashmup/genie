// Base template
// This file contains function declaration, file inclusion and
// common variable, methods

/* Created by Language version: 6.2.0 */
/* VECTORIZED */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "scoplib_ansi.h"
#undef PI
#define nil 0
#include "md1redef.h"
#include "section.h"
#include "nrniv_mf.h"
#include "md2redef.h"

#if METHOD3
extern int _method3;
#endif

#if !NRNGPU
#undef exp
#define exp hoc_Exp
extern double hoc_Exp(double);
#endif

#define _threadargscomma_ _p, _ppvar, _thread, _nt,
#define _threadargs_ _p, _ppvar, _thread, _nt

#define _threadargsprotocomma_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt,
#define _threadargsproto_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt
extern double *getarg();
/* Thread safe. No static _p or _ppvar. */

{{ global_variable }}

#if defined(__cplusplus)
extern "C" {
#endif

// function declarations
// not used
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_prop_size(int, int, int);
static void _modl_cleanup();
static int states(_threadargsproto_);

// function in xx_reg()
void _{{ filename }}_reg();
static void _initlists();
extern Symbol* hoc_lookup(const char*);
static void _thread_mem_init(Datum*);
extern void _nrn_setdata_reg(int, void(*)(Prop*));
extern void _nrn_thread_reg(int, int, void(*f)(Datum*));
extern void _nrn_thread_table_reg(int,void(*)(double*,
                                               Datum*,
                                               Datum*,
                                               _NrnThread*,
                                               int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
static void _check_table_thread(double* _p,
                                Datum* _ppvar,
                                Datum* _thread,
                                _NrnThread* _nt,
                                int _type);
static void _check_rates(double*, Datum*, Datum*, _NrnThread*);
static void _thread_mem_init(Datum* _thread);
static void _thread_cleanup(Datum*);
static void _update_ion_pointer(Datum*);
extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);

// TODO: user defined functions
// functions connected to hoc
static void _hoc_setdata();
static void _setdata(Prop* _prop);
static void _hoc_rates(void);
static int rates(_threadargsprotocomma_ double);
static int _f_rates(_threadargsprotocomma_ double);
static void _n_rates(_threadargsprotocomma_ double _lv);
static void _hoc_vtrap(void);
#define vtrap vtrap_{{ filename }}
extern double vtrap( _threadargsprotocomma_ double , double );

// functions for NEURON
static void nrn_alloc(Prop*);
extern Prop* need_memb(Symbol*);
extern void nrn_promote(Prop*, int, int);
static void nrn_init(_NrnThread*, _Memb_list*, int);
static void initmodel(_threadargsproto_);
static void nrn_state(_NrnThread*, _Memb_list*, int);
static void nrn_cur(_NrnThread*, _Memb_list*, int);
static void nrn_jacob(_NrnThread*, _Memb_list*, int);

// functions for CVODE
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
extern void _cvode_abstol( Symbol**, double*, int);
static void _ode_spec(_NrnThread*, _Memb_list*, int);
static int _ode_spec1(_threadargsproto_);
static void _ode_matsol(_NrnThread*, _Memb_list*, int);
static int _ode_matsol1(_threadargsproto_);

// Non used functions
static void _modl_cleanup(){
  _match_recurse=1;
}

{{ reg }}
{{ user_func }}
{{ ode_func }}
{{ neuron_func }}

#define exp hoc_Exp
static terminal(){}

#if defined(__cplusplus)
} /* extern "C" */
#endif
