# Example Datasets for Fortran AI

This directory contains sample datasets for training and testing AI models.

## Available Datasets

### 1. simple_data.csv
Simple regression data for testing linear regression models.
- **Columns**: x, y
- **Samples**: 10
- **Use**: Linear regression, basic testing

### 2. iris.csv
Classic Iris flower dataset for classification.
- **Columns**: sepal_length, sepal_width, petal_length, petal_width, species
- **Samples**: 150 (50 per class)
- **Classes**: Iris-setosa, Iris-versicolor, Iris-virginica
- **Use**: Multi-class classification, clustering

## Data Format

All CSV files follow this format:
- First row: Column headers
- Subsequent rows: Data values
- Separator: Comma (,)
- Decimal: Period (.)

## Loading Data in Fortran

### Reading CSV Files

```fortran
program read_csv
    implicit none
    integer :: unit, i, n_samples
    real, dimension(100) :: x, y
    character(len=100) :: header
    
    ! Open file
    open(newunit=unit, file='data/simple_data.csv', status='old')
    
    ! Skip header
    read(unit, *) header
    
    ! Read data
    n_samples = 0
    do
        n_samples = n_samples + 1
        read(unit, *, end=10) x(n_samples), y(n_samples)
    end do
    10 close(unit)
    
    n_samples = n_samples - 1
    print *, "Loaded", n_samples, "samples"
end program read_csv
```

## Adding Your Own Data

To add custom datasets:

1. Create a CSV file with headers
2. Place it in this directory
3. Update this README with description
4. Use consistent formatting (comma-separated, decimal point)

## Data Sources

- **Iris Dataset**: UCI Machine Learning Repository
- **Simple Data**: Synthetically generated for educational purposes

## License

These datasets are provided for educational purposes. Please check individual dataset licenses for redistribution rights.
