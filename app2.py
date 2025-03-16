import streamlit as st
import pandas as pd
import numpy as np
import time

# Initialize or load cloud resources
@st.cache_resource
def load_resources():
    return pd.DataFrame({
        "Resource_ID": range(1, 11),
        "CPU_Cores": np.random.randint(2, 16, size=10),
        "Memory_GB": np.random.randint(4, 64, size=10),
        "Storage_GB": np.random.randint(100, 500, size=10),
        "Allocated": ["No"] * 10,
        "VM_ID": [None] * 10  # Track which VM each resource is allocated to
    })

resources = load_resources()

# Virtual Machines DataFrame
@st.cache_resource
def load_vms():
    return pd.DataFrame(columns=["VM_ID", "CPU_Cores", "Memory_GB", "Storage_GB", "Status"])

vms = load_vms()

# Create a VM
def create_vm(cpu, memory, storage):
    new_id = len(vms) + 1
    vms.loc[new_id] = [new_id, cpu, memory, storage, "Running"]
    return new_id

# Function to allocate and deallocate resources
def allocate_resources(resource_id, vm_id):
    if resources.loc[resource_id - 1, 'Allocated'] == "No":
        resources.loc[resource_id - 1, 'Allocated'] = "Yes"
        resources.loc[resource_id - 1, 'VM_ID'] = vm_id
        return True
    return False

def deallocate_resources(resource_id):
    if resources.loc[resource_id - 1, 'Allocated'] == "Yes":
        vm_id = resources.loc[resource_id - 1, 'VM_ID']
        resources.loc[resource_id - 1, 'Allocated'] = "No"
        resources.loc[resource_id - 1, 'VM_ID'] = None
        if all(resources[resources['VM_ID'] == vm_id]['Allocated'] == "No"):
            vms.loc[vm_id, 'Status'] = "Stopped"
        return True
    return False

# Streamlit UI
st.title("Cloud Resource Allocation and VM Management Simulator")

# Sidebar for customization
st.sidebar.title("Customization Options")
show_resource_status = st.sidebar.checkbox("Show Resource Status")
show_vm_status = st.sidebar.checkbox("Show VM Status")
show_resource_utilization = st.sidebar.checkbox("Show Resource Utilization")
show_allocation_visualization = st.sidebar.checkbox("Show Allocation Visualization")

# VM creation
st.header("Create Virtual Machine")
vm_cpu = st.number_input("CPU Cores", min_value=1, value=2)
vm_memory = st.number_input("Memory (GB)", min_value=1, value=4)
vm_storage = st.number_input("Storage (GB)", min_value=10, value=100)
if st.button("Create VM"):
    vm_id = create_vm(vm_cpu, vm_memory, vm_storage)
    st.success(f"Virtual Machine {vm_id} created with {vm_cpu} CPU cores, {vm_memory} GB RAM, {vm_storage} GB Storage.")

# Resource allocation and deallocation
st.header("Manage Resources for VMs")
vm_list = vms['VM_ID'].dropna().unique()  # List of VMs that have been created
vm_id_select = st.selectbox("Select VM ID for resource allocation", options=vm_list)
resource_id = st.selectbox('Select Resource ID to Allocate/Deallocate', resources['Resource_ID'])
col1, col2 = st.columns(2)
with col1:
    if st.button('Allocate Resource'):
        if allocate_resources(resource_id, vm_id_select):
            st.success(f'Resource {resource_id} allocated to VM {vm_id_select}!')
        else:
            st.error("Resource already allocated!")
with col2:
    if st.button('Deallocate Resource'):
        if deallocate_resources(resource_id):
            st.success(f'Resource {resource_id} deallocated from VM!')
        else:
            st.error("Resource already deallocated!")

# Additional features based on customization
if show_resource_status:
    st.subheader('Resource Status')
    st.write(resources)

if show_vm_status:
    st.subheader('VM Status')
    st.write(vms)

if show_resource_utilization:
    st.subheader('Resource Utilization')
    # CPU Utilization Graph
    st.subheader("CPU Utilization")
    cpu_utilization = resources["CPU_Cores"] / resources["CPU_Cores"].sum() * 100
    st.bar_chart(cpu_utilization)

    # Memory Utilization Graph
    st.subheader("Memory Utilization")
    memory_utilization = resources["Memory_GB"] / resources["Memory_GB"].sum() * 100
    st.bar_chart(memory_utilization)

    # Storage Utilization Graph
    st.subheader("Storage Utilization")
    storage_utilization = resources["Storage_GB"] / resources["Storage_GB"].sum() * 100
    st.bar_chart(storage_utilization)

if show_allocation_visualization:
    st.subheader('Allocation Visualization')
    allocated_count = resources['Allocated'].value_counts()
    st.bar_chart(allocated_count)

# Resource utilization simulation
if st.checkbox("Simulate Resource Utilization"):
    with st.empty():
        for seconds in range(5):
            st.write(f"Simulating... {seconds + 1}")
            time.sleep(1)
    st.success("Simulation completed!")
