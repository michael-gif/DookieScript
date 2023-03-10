# DookieScript
Slightly annoying programming language

**Comparison with Python**

|                                   | Python  | DookieScript |
| --------------------------------- | ------- | ------------ |
| Readability                       | Good    | Meh          |
| Speed                             | Fast    | Fast         |
| Static or dynamic                 | Dynamic | Static       |
| Beginner friendly                 | Yes     | No           |
| Supports python modules/libraries | Yes     | Yes          |

### Available datatypes
| type    | dks type    |
| ------- | ----------- |
| int     | `<int>`     |
| float   | `<float>`   |
| string  | `<string>`  |
| boolean | `<boolean>` |
| null    | `<void>`    |
| unknown | `<?>`       |

### Available datastructures
- array
- immutable array (not implemented)
- set (not implemented)
- hashmap (not implemented)

### Operators
| operator        | dks operator |
| --------------- | ------------ |
| add/concat      | `+`          |
| subtract        | `-`          |
| multiply        | `*`          |
| divide          | `/`          |
| remainder       | `//`         |
| modulo          | `%`          |
| shorthand input | `<<`         |

### Language syntax
Imports
```
// all python modules are supported.

include module_name
include math
include pygame
```
Variables
```
container <int> age = 8

// static means constant. the variable value can't change
static container <string> name = "foo";

// if you want to do input, you have two options
container <string> fruit = call input("give a fruit")
container <string> fruit << "give a fruit"

// the second option uses the '<<' operator, which is just shorter
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
// for loop. only supports ++ and --
repeat (<int> start = 0, <int> stop = 10, start++) executes {
    // logic
}

// for-each loop
repeat:item (<datatype> element :=: iterable) executes {
    // logic
}

// while loop
repeat:item (condition) executes {
    // logic
}
```

Functions
```
'''
this is a docstring
the type specified after the '~' is the return type
in this case, the return type is <boolean>
'''
reusable foo(<int> param1, <string> param2) ~ <boolean> {
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
Write your dookie file, saving it with `.dks` as the extension. Example:

`numbergame.dks`
```
include random

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

Then run the DookieScript compiler `dksc.py`, passing the script file to `-dks <path>`:  
`python -m dksc -dks numbergame.dks`

You can specify an optional output file with `-out <path>` or `--out_file <path>`:  
`python -m dksc -dks numbergame.dks -out poop.py`