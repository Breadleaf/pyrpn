# PyRPN

A type-safe, decorator-driven RPN stack library for Python

## Features

- Intuitive stack syntax: `<<` to push `>>` to sink
- Strict decorator validation: `@stack_function` and `@StackProgram` validates at definition time
- Automatic snapshots & rollbacks: if a decorated function or operation fails, the stack will automatically rollback

## Examples

### Basic Stack Arithmetic

```
import pyrpn as p

# Build expressions using the shift operator
s = p.Stack() << 5 << 3 << p.sub
print(s) # Output: Stack([2])

# Chaining multiple operators
calc = p.Stack() << 4 << 9 << p.sqrt << p.add
print(calc) # Output: Stack([7.0])
```

### Writing Custom Stack Functions

```
import pyrpn as p

@p.stack_function(takes=1, returns=1)
def add_one(s: p.Stack) -> None:
  s << 1 << p.add

s = p.Stack() << 5
add_one.call(s)
print(s) # Output: Stack([6])
```

### Running Standalone Programs

```
import pyrpn as p

@p.StackProgram
def calculate_hypotenuse(s: p.Stack) -> None:
  # sqrt(3^2 + 4^2) = 5.0
  s << 3 << p.dup << p.mul
  s << 4 << p.dup << p.mul
  s << p.add << p.sqrt

result = calculate_hypotenuse.run()
# Output:
# running program: calculate_hypotenuse
# Stack([5.0])
```

### Sinking Results

```
import pyrpn as p

results = []
s = p.Stack() << 43
s >> results.append
print(results) # Output: [43]
print(s)       # Output: Stack([])
```

## License

Distributed under the MIT License. See LICENSE for more information.
