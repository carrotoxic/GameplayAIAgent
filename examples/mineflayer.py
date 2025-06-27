import minedojo

# Call make() with no args to get a sample task
env = minedojo.make(task_id="harvest_milk", image_size=(160, 256))

# List available task IDs
task_ids = env.TASK_ID_LIST

print(f"Total tasks: {len(task_ids)}")
for task_id in task_ids:
    if "harvest" in task_id:
        print(task_id)

obs = env.reset()
done = False
while not done:
    action = env.action_space.no_op()
    action["camera"] = [0, 10]  # turn right
    obs, reward, done, info = env.step(action)
    print("reward:", reward)
