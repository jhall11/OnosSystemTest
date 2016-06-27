Retry Function
-

Available from driver functions or test cases as utilities.retry, this function allows the test to retry a function when certain conditions are met.

The retry function takes several arguments:

        f        - a callable object such as a function
        retValue - Return value(s) of f to retry on. This can be a list or an
                   object.
        args     - A tuple containing the arguments of f.
        kwargs   - A dictionary containing the keyword arguments of f.
        sleep    - Time in seconds to sleep between retries. If random is True,
                   this is the max time to wait. Defaults to 1 second.
        attempts - Max number of attempts before returning. If set to 1,
                   f will only be called once. Defaults to 2 trys.
        random   - Boolean indicating if the wait time is random between 0
                   and sleep or exactly sleep seconds. Defaults to False.
