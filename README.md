# PyRPN

A type-safe, decorator-driven RPN stack library for Python

[github page](https://github.com/Breadleaf/pyrpn)

[pypi page](https://pypi.org/project/pyrpn-lib/)

## Features

- Intuitive stack syntax: `<<` to push `>>` to sink
- Strict decorator validation: `@stack_function` and `@StackProgram` validates at definition time
- Automatic snapshots & rollbacks: if a decorated function or operation fails, the stack will automatically rollback

## Examples

### Basic Stack Arithmetic

```
import pyrpn_lib as p

# Build expressions using the shift operator
s = p.Stack() << 5 << 3 << p.sub
print(s) # Output: Stack([2])

# Chaining multiple operators
calc = p.Stack() << 4 << 9 << p.sqrt << p.add
print(calc) # Output: Stack([7.0])
```

### Writing Custom Stack Functions

```
import pyrpn_lib as p

# function add_one (requires 1 item on stack) (will have a zero delta)
@p.stack_function(requires=1, delta=0)
def add_one(s: p.Stack) -> None:
  s << 1 << p.add

# function destroy (requires 1 item on stack) (will have a -1 delta)
@p.stack_function(requires=1, delta=-1)
def destroy(s: p.Stack) -> None:
  _ = s.items.pop()

s = p.Stack() << 5
add_one.call(s)
print(s) # Output: Stack([6])
destroy.call(s)
print(s) # Output: Stack([])
```

### Running Standalone Programs

```
import pyrpn_lib as p

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
import pyrpn_lib as p

results = []
s = p.Stack() << 43
s >> results.append
print(results) # Output: [43]
print(s)       # Output: Stack([])
```

## License

Distributed under the MIT License. See LICENSE for more information.
