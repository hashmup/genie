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
#define _gth 0
{{ define_global_param }}
#define htau_{{ filename }} _thread1data[0]
#define htau _thread[_gth]._pval[0]
#define hinf_{{ filename }} _thread1data[1]
#define hinf _thread[_gth]._pval[1]
#define mtau_{{ filename }} _thread1data[2]
#define mtau _thread[_gth]._pval[2]
#define minf_{{ filename }} _thread1data[3]
#define minf _thread[_gth]._pval[3]
#define ntau_{{ filename }} _thread1data[4]
#define ntau _thread[_gth]._pval[4]
#define ninf_{{ filename }} _thread1data[5]
#define ninf _thread[_gth]._pval[5]
#define usetable usetable_{{ filename }}
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

#define _cvode_ieq _ppvar[6]._i
/* connect range variables in _p that hoc is supposed to know about */
static const char *_mechanism[] = {
  "6.2.0",
  "{{ filename }}",
  "gnabar_{{ filename }}",
  "gkbar_{{ filename }}",
  "gl_{{ filename }}",
  "el_{{ filename }}",
  0,
  "gna_{{ filename }}",
  "gk_{{ filename }}",
  "il_{{ filename }}",
  0,
  "m_{{ filename }}",
  "h_{{ filename }}",
  "n_{{ filename }}",
  0,
  0
};
{{ ion_symbol }}
 /* some states have an absolute tolerance */
static Symbol** _atollist;
static HocStateTolerance _hoc_state_tol[] = {
  0,0
};

static double *_t_minf;
static double *_t_mtau;
static double *_t_hinf;
static double *_t_htau;
static double *_t_ninf;
static double *_t_ntau;
static int _reset;

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static int _slist1[3], _dlist1[3];
static double _mfac_rates, _tmin_rates;

#define KPLUS_WITHOUT_SHARED_CURRENT

#ifdef ARCH_K
#define BUFFER_SIZE 16000
#define MAX_NTHREADS 8
#else
#define BUFFER_SIZE 160000
#define MAX_NTHREADS 4
#endif


typedef double FLOAT;
#define EXP(x) exp((x))

#undef exp

#ifdef RESTRUCT_TABLE
#define TABLE_SIZE 201
FLOAT hh_table[TABLE_SIZE][6];
#define TABLE_N_TAU(x) hh_table[(x)][0]
#define TABLE_N_INF(x) hh_table[(x)][1]
#define TABLE_M_TAU(x) hh_table[(x)][2]
#define TABLE_M_INF(x) hh_table[(x)][3]
#define TABLE_H_TAU(x) hh_table[(x)][4]
#define TABLE_H_INF(x) hh_table[(x)][5]
#else
#define TABLE_N_TAU(x) _t_ntau[(x)]
#define TABLE_N_INF(x) _t_ninf[(x)]
#define TABLE_M_TAU(x) _t_mtau[(x)]
#define TABLE_M_INF(x) _t_minf[(x)]
#define TABLE_H_TAU(x) _t_htau[(x)]
#define TABLE_H_INF(x) _t_hinf[(x)]

#endif

/********************** NOTE ***********************
#define VEC_D(i) (_nt->_actual_d[(i)])
****************************************************/

static double _m_table[BUFFER_SIZE * MAX_NTHREADS];
static double _h_table[BUFFER_SIZE * MAX_NTHREADS];
static double _n_table[BUFFER_SIZE * MAX_NTHREADS];

static double _g_table[BUFFER_SIZE * MAX_NTHREADS];

static double _gnabar_table[BUFFER_SIZE * MAX_NTHREADS];
static double _gkbar_table[BUFFER_SIZE * MAX_NTHREADS];

static double _gl_table[BUFFER_SIZE * MAX_NTHREADS];
static double _ena_table[BUFFER_SIZE * MAX_NTHREADS];
static double _ek_table[BUFFER_SIZE * MAX_NTHREADS];
static double _el_table[BUFFER_SIZE * MAX_NTHREADS];
static double _il_table[BUFFER_SIZE * MAX_NTHREADS];

static double _v_table[BUFFER_SIZE * MAX_NTHREADS];

#ifndef KPLUS_WITHOUT_SHARED_CURRENT
static double _gna_table[BUFFER_SIZE * MAX_NTHREADS];
static double _gk_table[BUFFER_SIZE * MAX_NTHREADS];
static double _ina_table[BUFFER_SIZE * MAX_NTHREADS];
static double _ik_table[BUFFER_SIZE * MAX_NTHREADS];
#endif

#if defined(__cplusplus)
} /* extern "C" */
#endif
