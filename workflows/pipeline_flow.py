from prefect import flow, task


@task
def say_hello(name: str) -> str:
    message = f"Hello, {name}!"
    print(message)
    return message


@flow(name="hello-world")
def hello_flow(name: str = "Hackathon"):
    result = say_hello(name)
    print(f"Flow complete: {result}")


if __name__ == "__main__":
    hello_flow()
