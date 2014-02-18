class Main inherits IO {
  main() : Object {
    let
      stop : Int <- 500,
      i : Int <- 0,
      done : Bool <- false
    in {
      out_string("Hello, world.\n");

      "" -- Problematic

      -- Binary ops
      i <- i + 550;
      i <- i - 15;
      i <- i * 5;
      i <- i / 10;
      
    }
  };