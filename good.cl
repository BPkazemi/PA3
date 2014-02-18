class Main inherits IO {
  main() : Object {
    let
      stop : Int <- 500,
      i : Int <- 0,
      done : Bool <- false,
      matched : Bool <- false,
      str : String <- "b"
    in {
      out_string("Hello, world.\n");

      -- Assignment and loops
      while i < stop loop
      {
        i <- i + 1;
      } pool;

      if i = 500 then {
        done <- true;
      }
      else {
        done <- false;
      }
      fi;

      case str of
         a : String => matched <- false;
         b : String => matched <- true;
      esac;

      -- Binary ops
      i <- i + 550;
      i <- i - 15;
      i <- i * 5;
      i <- i / 10;
    }
  } ;

  other() : Object {
    out_string("Hello, again..\n")
  } ;


  test : Int <- new Blah;

  (* Here are some comments
    (* Nested ones, too! *)
    -- blah blah 


    blah 

    *)


} ;