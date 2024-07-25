import sys
import time

def main():
    # Simulate a task that takes time and outputs progress
    for i in range(11):
        # Print progress to stdout
        print(i)
        # sys.stdout.flush()  # Ensure the output is flushed immediately
        time.sleep(1)  # Simulate work being done

    print("done")

if __name__ == "__main__":
    main()