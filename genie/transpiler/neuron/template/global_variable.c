// User defined variables
#define t _nt->_t
#define dt _nt->_dt
{{ define_params }}
{{ define_ions }}

#if MAC
#if !defined(v)
#define v _mlhv
#endif
#if !defined(h)
#define h _mlhh
#endif
#endif

#if defined(__cplusplus)
extern "C" {
#endif

static char *modelname = "{{ title }}";

static int hoc_nrnpointerindex =  -1;
static Datum* _extcall_thread;
static Prop* _extcall_prop;
/* external NEURON variables */
extern double celsius;

// function declaration
/* declaration of user functions */
static int _mechtype;
extern Memb_func* memb_func;

/* declare global and static user variables */
static int _thread1data_inuse = 0;
static double _thread1data[{{ num_global_param }}];
{{ define_global_param }}
double usetable = 1;

/* some parameters have upper and lower limits */
static HocParmLimits _hoc_parm_limits[] = {
{{ hoc_parm_limits }}
};
static HocParmUnits _hoc_parm_units[] = {
{{ hoc_parm_units }}
};
/* connect global user variables to hoc */
static DoubScal hoc_scdoub[] = {
{{ hoc_global_param }}
};
static DoubVec hoc_vdoub[] = {
  0,0,0
};
static double delta_t = 0.01;
static double h0 = 0;
static double m0 = 0;
static double n0 = 0;

static double _sav_indep;

#define _cvode_ieq _ppvar[{{ num_cvode }}]._i
/* connect range variables in _p that hoc is supposed to know about */
static const char *_mechanism[] = {
{{ mechanism }}
};
{{ ion_symbol }}
 /* some states have an absolute tolerance */
static Symbol** _atollist;
static HocStateTolerance _hoc_state_tol[] = {
  0,0
};

{{ static_global }}
static int _reset;

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static int _slist1[{{ num_states }}], _dlist1[{{ num_states }}];
static double _mfac_rates, _tmin_rates;

#ifdef ARCH_K
#define BUFFER_SIZE 16000
#define MAX_NTHREADS 8
#else
#define BUFFER_SIZE 8000
#define MAX_NTHREADS 16
#endif

typedef double FLOAT;
#define EXP(x) exp((x))

#undef exp

{{ restruct_table }}

/********************** NOTE ***********************
#define VEC_D(i) (_nt->_actual_d[(i)])
****************************************************/
{{ optimize_table }}
#if defined(__cplusplus)
} /* extern "C" */
#endif
