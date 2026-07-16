import json
import sys


def main():
    import flow_build_manager
    if len(sys.argv) != 3:
        print("Usage: python main_build.py <env> <tier>")
        print("<env>: dev | uat | prod")
        print("<tier>: free or pro")
        return

    env = sys.argv[1]
    tier = sys.argv[2]

    if env not in ['dev', 'uat', 'prod']:
        print('The env parameter must be either "dev | uat | prod".')
        return

    if tier not in ['free', 'pro']:
        print('The tier parameter must be either "free" or "pro".')
        return

    # Update constant.json with mode and tier
    with open('constant.json', 'r') as file:
        data = json.load(file)

    data['env'] = env
    data['tier'] = tier

    with open('constant.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Run the build process
    flow_build_manager.prepareWork()


if __name__ == '__main__':
    main()