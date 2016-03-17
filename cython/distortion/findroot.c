
#include <stdio.h>
#include <math.h>

#define MAXROOT 3000000
#define FOURPI_BY_THREE 
#define MINROOT -3000000
#define MAX_ITERATIONS 1000
#define CONVERGE_LIMIT 1e-12

/* find the radius using Newton's method , adapted from Numerical Recipes in C by Press and Flannery */

double find_new_radius (double a, double b, double c, double d, double r)
{
  double f, df, dx, sigma, rold,rzero;
  int i;
  rzero=r;


  for (i = 0; i < MAX_ITERATIONS; i++) {
    f = a*r + b*r*r + c*r*r*r +d*r*r*r*r-rzero;
    df =  a + 2.0*b*r + 3.0*c*r*r + 4*d*r*r*r ; 
    dx = f / df;
    rold = r;
    r -= dx;
#ifdef TEST_FINDROOT
    printf ("r: %.10g, r-rold %.10g, (r-rold/rold) %.10g\n", r, r-rold, (r - rold)/rold);
#endif

    if ((MAXROOT - r) * (r - MINROOT) < 0.0) {
#ifdef ERROR_EXIT
      fprintf (stderr, "ERROR: find_new_radius: exceeded bounds on radius.\n");
      exit (10);
#endif
#ifdef TEST_FINDROOT
      printf ("Returning due to bounds on radius.\n");
#endif
      return (r);
    }
    if (fabs ((r - rold)/rold) < CONVERGE_LIMIT) {
#ifdef TEST_FINDROOT
      printf ("Niter: %i\n", i);
#endif
#ifdef TEST_FINDROOT
      printf("Returning due to convergence criterion\n");
#endif
      return (r);
    }
  }
#ifdef ERROR_EXIT
  fprintf (stderr, "ERROR: find_new_radius: exceeded maximum iterations.\n");
  exit (10);
#endif
  return (r);
}

#ifdef TEST_FINDROOT_MAIN
void main ()
{
  double a,b,c,d, r, rNew;
  double f;
  float rin;
  a=.99;
  b=1e-5;
  c=1e-7;
  d=1e-9;


  for (;;) {
    printf ("r_dist:\n");
    scanf ("%f", &rin);
    r=(double)(rin);
    printf ("Rold = %.5g\n", r);
    rNew = find_new_radius (a,b,c,d, r);
    f = a*rNew + b*rNew*rNew + c*rNew*rNew*rNew +d*rNew*rNew*rNew*rNew;
    printf ("Rnew = %g f=%g\n", rNew,f);
  }

}
#endif /*TEST_FINDROOT_MAIN*/

/* Little subroutine to get rcs id into the object code */
/* so you can use ident on the compiled program  */
/* also you can call this to print out or include the rcs id in a file */
char const *rcs_id_findroot_c ()
{
  static char const rcsid[] = "$Id: findroot.c 393 2015-10-05 14:02:11Z kny48981 $";

  return (rcsid);
}

/* end of rcs_id_subroutine */
