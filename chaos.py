import boto3
import json
import random
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

lambda_client = boto3.client('lambda', region_name=os.getenv('AWS_REGION'))
cloudwatch = boto3.client('cloudwatch', region_name=os.getenv('AWS_REGION'))

def get_all_lambda_functions():
    print("🔍 Discovering Lambda functions...")
    functions = []
    paginator = lambda_client.get_paginator('list_functions')
    
    for page in paginator.paginate():
        for func in page['Functions']:
            functions.append({
                'name': func['FunctionName'],
                'arn': func['FunctionArn'],
                'runtime': func.get('Runtime', 'unknown'),
                'memory': func['MemorySize'],
                'timeout': func['Timeout']
            })
    
    print(f"Found {len(functions)} Lambda function(s)\n")
    return functions

def inject_failure(function_name, failure_type='throttle'):
    print(f"💥 Injecting {failure_type} failure into {function_name}...")
    
    experiment = {
        'timestamp': datetime.now().isoformat(),
        'function': function_name,
        'failure_type': failure_type,
        'status': 'unknown'
    }
    
    try:
        if failure_type == 'throttle':
            # Set concurrency to 0 — throttles all invocations
            lambda_client.put_function_concurrency(
                FunctionName=function_name,
                ReservedConcurrentExecutions=0
            )
            experiment['status'] = 'success'
            experiment['action'] = 'Set reserved concurrency to 0'
            print(f"✅ Throttled {function_name} — concurrency set to 0")
            
        elif failure_type == 'memory_stress':
            # Reduce memory to minimum
            config = lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            original_memory = config['MemorySize']
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                MemorySize=128
            )
            experiment['status'] = 'success'
            experiment['action'] = f'Reduced memory from {original_memory}MB to 128MB'
            experiment['original_memory'] = original_memory
            print(f"✅ Memory stress applied to {function_name}")

    except Exception as e:
        experiment['status'] = 'failed'
        experiment['error'] = str(e)
        print(f"❌ Failed to inject failure: {e}")
    
    return experiment

def recover_function(function_name, experiment):
    print(f"🔄 Recovering {function_name}...")
    
    try:
        if experiment.get('failure_type') == 'throttle':
            # Remove concurrency limit
            lambda_client.delete_function_concurrency(
                FunctionName=function_name
            )
            print(f"✅ {function_name} recovered — concurrency restored")
            
        elif experiment.get('failure_type') == 'memory_stress':
            # Restore original memory
            original_memory = experiment.get('original_memory', 256)
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                MemorySize=original_memory
            )
            print(f"✅ {function_name} recovered — memory restored to {original_memory}MB")
            
        return True
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        return False

def run_chaos_experiment(target_function=None, failure_type='throttle', duration=30):
    print("🐒 Chaos Monkey Jr.")
    print("==================\n")
    
    # Get all functions
    functions = get_all_lambda_functions()
    
    if not functions:
        print("No Lambda functions found to chaos test!")
        return
    
    # Pick target
    if target_function:
        target = next((f for f in functions if f['name'] == target_function), None)
        if not target:
            print(f"Function {target_function} not found!")
            return
    else:
        # Randomly pick one
        target = random.choice(functions)
    
    print(f"🎯 Target: {target['name']}")
    print(f"💥 Failure type: {failure_type}")
    print(f"⏱️  Duration: {duration} seconds\n")
    
    # Inject failure
    start_time = time.time()
    experiment = inject_failure(target['name'], failure_type)
    
    if experiment['status'] == 'success':
        print(f"\n⏳ Chaos active for {duration} seconds...")
        print("In production this is when you'd monitor your alerts and dashboards")
        time.sleep(duration)
        
        # Recover
        recovery_start = time.time()
        recovered = recover_function(target['name'], experiment)
        recovery_time = time.time() - recovery_start
        total_time = time.time() - start_time
        
        experiment['recovered'] = recovered
        experiment['recovery_time_seconds'] = round(recovery_time, 2)
        experiment['total_experiment_duration'] = round(total_time, 2)
        
        print(f"\n📊 EXPERIMENT RESULTS:")
        print(f"Target function: {target['name']}")
        print(f"Failure type: {failure_type}")
        print(f"Recovery time: {recovery_time:.2f} seconds")
        print(f"Total duration: {total_time:.2f} seconds")
        print(f"Recovery status: {'✅ Success' if recovered else '❌ Failed'}")
    
    # Save report
    report = {
        'experiment': experiment,
        'target_function': target,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('chaos_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to chaos_report.json")
    print("\n✅ Chaos experiment complete!")
    
    return report

if __name__ == "__main__":
    # Target our morning bot for chaos testing
    run_chaos_experiment(
        target_function='ai-morning-bot',
        failure_type='throttle',
        duration=10
    )