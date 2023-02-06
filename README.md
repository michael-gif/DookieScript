# DooDooScript
My own programming language

### Available datatypes
- int
- float
- string
- boolean

### Available datastructures
- array
- immutable array (not implemented)
- set (not implemented)
- hashmap (not implemented)

### Operators
- add/concat -> +
- subtract -> -
- multiply -> *
- divide -> /
- remainder -> //
- modulo -> %

### Language syntax
Variables
```
container <int> age = 8

// static means constant. the variable value can't change
static container <string> name = "foo";
```
Arrays
```
multipart <int> ages = {7, 8};

// again, static means constant.
static multipart <string> names = {"foo", "bar"}
```

Conditionals
```
query (condition) executes {
    // logic
}

// not implemented yet
query (condition) executes {
    // logic
} otherwise {
    // logic
}

// not implemented yet
query (condition) executes {
    // logic
} otherwise query (condition2) executes {
    // logic
} otherwise {
    // logic
}
```

Loops
```
// not implemented yet
repeat (<int> start, <int> stop, <int> index) {
    // logic
}

repeat query (condition) {
    // logic
}
```

Functions
```
'''
this is a docstring
'''
reusable foo(<int> param1, <string> param2) returns <boolean> {
    // logic
    return true;
}
```

Calling a function
```
call foo(42, "bar");
```

Comments
```
// this is a comment
/*
this is a multiline comment
*/
```

## Usage
Write your doodoo file, saving it with `.dds` as the extension. Example:

`numbergame.dds`
```
// computer picks random number from 1 to 10, player picks random number from 1 to 10, whoever picked highest wins.

'''
Get the computer's number using a random number generator.
'''
reusable getComputerNumber(<int> a, <int> b) returns <int> {
    return call random.int(1, 10);
}

'''
Get the player's number using input. Make sure the input is a number between 1 and 10.
'''
reusable getPlayerNumber() returns <int> {
    repeat query (true) {
        static container <int> playerNumber << "Enter a number from 1 to 10";
        query (1 <= playerNumber <= 10) executes {
            return playerNumber;
        } otherwise {
            print("Number must be from 1 to 10");
        }
    }
}

'''
Game logic.
If both numbers are equal, it is a draw.
If the computer's number is higher, computer wins.
If the player's number is higher, player wins.
'''
reusable main() return void {
    static container <string> computerNumber = call getComputerNumber();
    static container <string> playerNumber = call getPlayerNumber();
    query (computerNumber == playerNumber) executes {
        print("Draw");
        return;
    }
    query (computerNumber > playerNumber) executes {
        print("Computer wins");
        return;
    }
    query (computerNumber <= playerNumber) executes {
        print("Player wins");
        return;
    }
}

call main()
```

Then run main.py, giving it the filename as the first argument:
`python -m main.py -dds numbergame.dds`

The doodoo file will be tokenized, converted to python, and run.