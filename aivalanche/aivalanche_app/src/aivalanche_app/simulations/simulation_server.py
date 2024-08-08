import zmq, queue, pickle, sys, signal
from multiprocessing import Process, Queue
from aivalanche_app.simulations.model_calibration import model_calibration

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

calibrations = {}

def get_result(q):        
    # Fetch all the items in the queue and use return only the last one.
    items = []
    while not q.empty():
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            break  # This shouldn't happen, but just in case
    
    item = None
    if len(items) > 0:
        item = items[-1]
        item['better_solution_found'] = any([x['better_solution_found'] for x in items])
    
    return item

def run_calibration(calibration_id, simulation_input, result_queue, command_queue):
    calibration = model_calibration(result_queue = result_queue, command_queue = command_queue)
    calibration.update_simulation_input(simulation_input)
    calibration.run()

def signal_handler(sig, frame):
    print("\nCtrl+C pressed. Cleaning up and exiting...")
    for cal_id, cal_data in calibrations.items():
        print(f"Terminating calibration {cal_id}")
        cal_data['command_queue'].put('abort')
        cal_data['process'].join(timeout=5)
        if cal_data['process'].is_alive():
            print(f"Calibration {cal_id} didn't terminate gracefully. Forcing termination.")
            cal_data['process'].terminate()
    
    socket.close()
    context.term()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    message = pickle.loads(socket.recv())
    command = message['command']
    
    # Decode and unpickle the simulation input
    if 'simulation_input' in message:
        simulation_input = message['simulation_input']
    
    if command == 'start_calibration':
        calibration_id = message['calibration_id']
        simulation_input = message['simulation_input']
        result_queue = Queue()
        command_queue = Queue()
        process = Process(target = run_calibration, args = (calibration_id, simulation_input, result_queue, command_queue))
        process.start()
        calibrations[calibration_id] = {'process': process, 'result_queue': result_queue, 'command_queue': command_queue}
        socket.send(pickle.dumps({"status": "calibration_started"}))
    elif command == 'abort_calibration':
        calibration_id = message['calibration_id']
        if calibration_id in calibrations:
            calibrations[calibration_id]['command_queue'].put('abort')
            socket.send(pickle.dumps({"status": "calibration_abort_sent"}))
        else:
            socket.send(pickle.dumps({"status": "not_found"}))
    elif command == 'check_calibration_status':
        calibration_id = message['calibration_id']
        if calibration_id in calibrations:
            result = get_result(q = calibrations[calibration_id]['result_queue'])
            socket.send(pickle.dumps(result))
            if result is not None:
                status = result['status']
                if status  == 'finish':
                    calibrations[calibration_id]['process'].join()
                    del calibrations[calibration_id]
        else:
            socket.send(pickle.dumps({"status": "not_found"}))
    elif command == 'start_single_simulation':
        single_simulation_id = message['calibration_id']
        simulation_input = message['simulation_input']
        result_queue = Queue()
        command_queue = Queue()
        process = Process(target = run_calibration, args = (calibration_id, simulation_input, result_queue, command_queue))
        process.start()
        calibrations[calibration_id] = {'process': process, 'result_queue': result_queue, 'command_queue': command_queue}
        socket.send(pickle.dumps({"status": "single_simulation_started"}))
    else:
        socket.send(pickle.dumps({"status": "unknown_command"}))

