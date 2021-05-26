To start the project:
===============================

1.Download Anaconda and install the Anaconda installer
  https://www.anaconda.com/products/individual#Downloads

2. Install and add an environment variable to the path.
   A local variable can be added to the path prior to installation in the wizard, or later in an anaconda client.

3. Create a virtual environment using requirements.yml
   Can yous anaconda client to create a new virtual environment, select requirements.yml file, and click ok.
   Alternatively, in windows can use the command line and type "conda env create -f requirements.yml"

4. Activate virtual environment using command "conda activate fyp_k00232104_venv"

5. Navigate to the project's directory, where manage.py file is located.

6. Use the command "python manage.py runserver"

7. Navigate to "http://127.0.0.1:8000/" in your browser

8. You should be greeted with the login form. Use the following credentials:
   Email: testuser@gmail.com
   Password: testpassword


To produce Predictions
====================================
In the project's directory navigate to Utils folder, you should see files ARIMA.py and LSTM.py.

To produce LSTM predictions you will need to uncomment the last line where the call to apply_lstm() function is.
Type in a company symbol you would like to get predictions for and run the file. If the model for this symbol was trained
already, the process will be faster, otherwise, it will take between 2 to 4 minutes. Once compiling is done you should see a
plot with predictions for the next 10 days. It will be saved as png with symbol name in Utils/plots/lstm directory.

To produce ARIMA prediction. Uncomment the last four lines in the file ARIMA.py. You can change the symbol and how many days
you wish to predict. You will notice 2 function calls:
    predictions_only(symbol, days_to_predict) - this will plot predictions for the future
    predictions_with_testing(symbol, days_to_predict) - this will roll back the number of days you wish to predict,
    and will plot predictions together with actual prices for the last days.
