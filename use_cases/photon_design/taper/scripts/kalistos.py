import random

def generate_taper_file(filename, min_val=0.01, max_val=10):
    # Template for the file content
    template = '''begin <FPOptimiser(1.2)> "kallistos-taper"
  PRJITEMNAME : "example_taper"
  PRECISION : 0.0001
  MAXFUNCEVALS : 0
  MAXIMISE : 1
  OPTMETHOD : 1
  OBJFUNCTYPE : Mode Power(1)
  ANALYTICMETHOD : 1
  BOXSIZE : 0.000000'''

    # Generate random values for w1 through w9
    random_values = [random.uniform(min_val, max_val) for _ in range(9)]

    # Add the INDEPENDENTVAR lines with random values
    for i, value in enumerate(random_values, 1):
        template += f'\n  INDEPENDENTVAR : w{i} {min_val} {max_val} {value:.2f}'

    # Add the ending
    template += '\nend'

    # Write to file
    with open(filename, 'w') as f:
        f.write(template)

# Usage example
generate_taper_file('kalistos_config.txt')
