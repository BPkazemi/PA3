class Main inherits IO {
  main() : Object {
    out_string("Hello, world.\n")
  } ;
  main() : Object {
    out_string("Hello, world.\n")
  } ;

  testee : Int <- 4;

  out : Int <-		-- out is our 'output'.  Its values are the primes.
    {
      out_string("2 is trivially prime.\n");
      2;
    };

} ;
