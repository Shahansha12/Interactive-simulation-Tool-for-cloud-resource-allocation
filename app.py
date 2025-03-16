import streamlit as st
import json
from threading import Lock
import uuid

class ResourceManager:
    def __init__(self):
        self.lock = Lock()
        self.resources = self.load_json('resources.json', {'cpu': {'total': 100, 'available': 100}, 'memory': {'total': 256, 'available': 256}, 'storage': {'total': 1000, 'available': 1000}})
        self.pools = self.load_json('pools.json', {})

    def load_json(self, file_path, default_data):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(file_path, 'w') as file:
                json.dump(default_data, file)
            return default_data

    def save_json(self, file_path, data):
        with self.lock:
            with open(file_path, 'w') as file:
                json.dump(data, file)

    def create_vm(self, cpu, memory, storage):
        with self.lock:
            if all(self.resources[k]['available'] >= v for k, v in [('cpu', cpu), ('memory', memory), ('storage', storage)]):
                for k, v in [('cpu', cpu), ('memory', memory), ('storage', storage)]:
                    self.resources[k]['available'] -= v
                self.save_json('resources.json', self.resources)
                vm_id = str(uuid.uuid4())
                return f"VM {vm_id} created successfully with CPU: {cpu}, Memory: {memory}, Storage: {storage}."
            else:
                return "Insufficient resources to create VM."

    def create_pool(self, name, cpu, storage):
        with self.lock:
            if name in self.pools:
                print(f"Requested - CPU: {cpu}, Memory: {storage}, Storage: {storage}")
                print(f"Available - CPU: {self.resources['cpu']['available']}, Memory: {self.resources['memory']['available']}, Storage: {self.resources['storage']['available']}")
                return "Pool already exists."
            if all(self.resources[k]['available'] >= v for k, v in [('cpu', cpu), ('memory', storage)]):
                for k, v in [('cpu', cpu), ('memory', storage)]:
                    self.resources[k]['available'] -= v
                self.pools[name] = {'cpu': cpu, 'memory': storage}
                self.save_json('pools.json', self.pools)
                return f"Pool {name} created successfully with CPU: {cpu}, Memory: {storage}."
            else:
                return "Insufficient resources to create pool."

    def adjust_resources(self, source_pool, target_pool, cpu, memory):
        with self.lock:
            if source_pool not in self.pools or target_pool not in self.pools:
                return "One or both pools do not exist."
            if all(self.pools[source_pool]['cpu'] >= cpu and self.pools[source_pool]['memory'] >= memory):
                for k, v in [('cpu', cpu), ('memory', memory)]:
                    self.pools[source_pool][k] -= v
                    self.pools[target_pool][k] += v
                self.save_json('pools.json', self.pools)
                return f"Moved {cpu} CPU and {memory} Memory from {source_pool} to {target_pool}."
            else:
                return "Insufficient resources in source pool."

# Streamlit Interface Setup and Resource Management System
def setup_interface():
    st.title('Cloud Resource Manager')
    manager = ResourceManager()

    with st.form("create_vm"):
        st.subheader("Create a Virtual Machine")
        cpu = st.number_input('CPU units', min_value=1, step=1, value=1)
        memory = st.number_input('Memory (GB)', min_value=1, step=1, value=1)
        storage = st.number_input('Storage (GB)', min_value=1, step=1, value=1)
        submit_vm = st.form_submit_button('Create VM')
        if submit_vm:
            result = manager.create_vm(int(cpu), int(memory), int(storage))
            st.success(result)

    with st.form("manage_pools"):
        st.subheader("Manage Resource Pools")
        action = st.radio("Choose action:", ['Create Pool', 'Adjust Resources'])
        if action == 'Create Pool':
            pool_name = st.text_input('Pool Name')
            pool_cpu = st.number_input('Pool CPU units', min_value=1, step=1, value=1)
            pool_memory = st.number_input('Pool Memory (GB)', min_value=1, step=1, value=1)
            submit_pool = st.form_submit_button('Create Pool')
            if submit_pool:
                result = manager.create_pool(pool_name, int(pool_cpu), int(pool_memory))
                st.success(result)
        elif action == 'Adjust Resources':
            source_pool = st.selectbox('Source Pool', list(manager.pools.keys()))
            target_pool = st.selectbox('Target Pool', list(manager.pools.keys()))
            cpu_transfer = st.number_input('CPU units to transfer', min_value=0, step=1, value=1)
            memory_transfer = st.number_input('Memory (GB) to transfer', min_value=0, step=1, value=1)
            submit_adjust = st.form_submit_button('Adjust Resources')
            if submit_adjust:
                result = manager.adjust_resources(source_pool, target_pool, int(cpu_transfer), int(memory_transfer))
                st.success(result)

if __name__ == "__main__":
    setup_interface()
