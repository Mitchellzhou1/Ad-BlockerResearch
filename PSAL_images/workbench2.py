import multiprocessing

# Function to be executed by the processes
def process_func(packet_dict):
    nested_dict = packet_dict["nested_dict"]
    nested_dict["key"] = "value"

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    packet_dict = manager.dict()
    packet_dict["nested_dict"] = manager.dict()

    # Create and start the process
    process = multiprocessing.Process(target=process_func, args=(packet_dict,))
    process.start()
    process.join()

    # Print the modified packet_dict after the process
    print(packet_dict["nested_dict"].values())
