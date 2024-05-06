from multiprocessing import Process, Event, Value

# Function to yield a value after waiting
def waiter(event, value):
    print("Waiter is waiting...")
    event.wait()  # Wait for the event to be set
    print("Waiter received value:", value.value)

# Function to set the event and yield a value
def notifier(event, value):
    print("Notifier is notifying...")
    value_to_yield = "Hello, waiter!"
    value.value = value_to_yield  # Update the shared value object
    event.set()  # Set the event to notify the waiter

if __name__ == "__main__":
    # Create an Event for synchronization
    event = Event()

    # Create a shared Value object for passing values between processes
    shared_value = Value('i', 0)

    # Create two processes - waiter and notifier
    waiter_process = Process(target=waiter, args=(event, shared_value))
    notifier_process = Process(target=notifier, args=(event, shared_value))

    # Start the notifier process
    notifier_process.start()
    notifier_process.join()

    # Start the waiter process
    waiter_process.start()
    waiter_process.join()
