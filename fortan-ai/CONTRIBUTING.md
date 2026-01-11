# Contributing to Fortran AI

Thank you for your interest in contributing to the Fortran AI project! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

- Check if the issue already exists in the issue tracker
- Provide a clear description of the problem
- Include:
  - Your operating system and compiler version
  - Steps to reproduce the issue
  - Expected vs actual behavior
  - Error messages or output

### Suggesting Enhancements

- Describe the enhancement clearly
- Explain why it would be useful
- Provide examples if applicable

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding style guidelines below
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   make clean
   make all
   make test
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: brief description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Describe what you changed and why
   - Reference any related issues

## Coding Style Guidelines

### Fortran Code

1. **Use Modern Fortran** (2008/2018 standard)
   ```fortran
   ! Good
   implicit none
   real, dimension(:), allocatable :: array
   
   ! Avoid
   real array(100)  ! Fixed size
   ```

2. **Always use `implicit none`**
   ```fortran
   program my_program
       implicit none
       ! Your code here
   end program my_program
   ```

3. **Use meaningful variable names**
   ```fortran
   ! Good
   real :: learning_rate, gradient, weight
   
   ! Avoid
   real :: lr, g, w
   ```

4. **Add comments for clarity**
   ```fortran
   ! Calculate the weighted sum: z = w·x + b
   z = dot_product(weights, inputs) + bias
   ```

5. **Use lowercase for code**
   ```fortran
   ! Good
   subroutine train_network(...)
   
   ! Avoid
   SUBROUTINE TRAIN_NETWORK(...)
   ```

6. **Indent consistently** (4 spaces recommended)
   ```fortran
   do i = 1, n
       if (condition) then
           call some_subroutine()
       end if
   end do
   ```

7. **Use intent for procedure arguments**
   ```fortran
   subroutine process(input, output, buffer)
       real, intent(in) :: input
       real, intent(out) :: output
       real, intent(inout) :: buffer
   ```

### Documentation

1. **Document new features** in the appropriate `docs/` file
2. **Update README.md** if you add new examples
3. **Add code comments** explaining complex algorithms
4. **Include usage examples** for new functions/modules

### File Organization

- **Beginner examples**: `src/01-beginner/`
- **Intermediate examples**: `src/02-intermediate/`
- **Advanced examples**: `src/03-advanced/`
- **Applications**: `src/04-applications/`
- **Utilities**: `src/utils/`
- **Complete examples**: `examples/`
- **Documentation**: `docs/`
- **Data**: `data/`

## What to Contribute

### Most Needed

1. **More examples**
   - Intermediate level neural networks
   - Advanced CNN/RNN implementations
   - Real-world applications

2. **Documentation improvements**
   - Clarify existing docs
   - Add diagrams
   - More code examples

3. **Performance optimizations**
   - Use BLAS/LAPACK
   - OpenMP parallelization
   - Algorithm improvements

4. **Testing**
   - Unit tests
   - Integration tests
   - Validation scripts

### Ideas for New Features

- Image processing examples
- Time series analysis
- Reinforcement learning
- AutoML capabilities
- Visualization tools
- Data preprocessing utilities
- Model serialization/deserialization
- Benchmarking suite

## Testing

Before submitting:

1. **Compile without warnings**
   ```bash
   gfortran -Wall -std=f2008 -o test your_code.f90
   ```

2. **Test your code**
   ```bash
   ./test
   ```

3. **Verify existing examples still work**
   ```bash
   make clean
   make all
   make test
   ```

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your code will be merged
4. Your contribution will be acknowledged!

## Questions?

- Open an issue for questions
- Check existing documentation first
- Be patient - this is an educational project

## Recognition

All contributors will be acknowledged in the project. Thank you for helping make Fortran AI better!

---

Happy contributing! 🚀
