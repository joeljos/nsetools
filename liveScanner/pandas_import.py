import pandas as pd
import os

# ~/Library/Caches/nsehistory-stock

def import_dataframes_from_directory(directory="/Users/joeljos/Library/Caches/nsehistory-stock"):
  """Imports all the Pandas DataFrames from a directory.

  Args:
    directory: The directory containing the Pandas DataFrames.

  Returns:
    A Pandas DataFrame containing all the data from the directory.
  """

  # Create a list of all the file names in the directory.
  file_names = os.listdir(directory)

  # Iterate over the list of file names and read each file into a Pandas DataFrame.
  dataframes = []
  for file_name in file_names:
    dataframes.append(pd.read_csv(os.path.join(directory, file_name)))

  # Concatenate all the DataFrames into a single DataFrame.
  dataframe = pd.concat(dataframes)

  # Return the single DataFrame.
  return dataframe

