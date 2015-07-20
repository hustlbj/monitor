namespace py    crane.thrift

service IaaSService{    

    string get_auth(1:string u_name ),

    string usercreatekeys(1:string username, 2:string keyname), 

    string userdelkeys(1:string username, 2:string keyname),     

    string querykeys(1:string username),    

    string downloadkeys(1:string username, 2:string keyname),

    string get_hostpool_info(),               

    string get_host_info(1:i32 host_id), 

    string host_create(1:string host, 2:string vmm),

    string host_delete(1:i32 host_id),

    string get_user_list(),               

    string user_create(1:string user),  

    string user_delete(1:string user),         

    string init_user(1:string user),        

    string get_uid(1:string user),

    string get_imagepool_info(1:string user),        

    string get_image_info(1:string user),

    string get_all_vmpool_info(1:string user),           

    string get_vms_host(1:string host_name),       

    string get_vmpool_info(1:string user, 2:string flag ),              

    string get_vms_info(1:i32 flag , 2:i32 template ),     

    string run_remote_command(1:string user, 2:i32 vm_id, 3:string command),       

    string get_vm_status(1:i32 vm_id),       

    string vm_action(1:string user, 2:string action, 3:i32 vm_id),              

    string vm_create(1:string HVM), // HVM              

    string vm_create_details(1:string user_name, 2:i32 memory, 3:i32 vcpu, 4:string image_dir, 5:i32 count, 6:string userkey, 7:string start, 
    8:string duration , 9:string meepo ),

    string vm_delete(1:string user, 2:i32 vm_id),

    string vm_destroy(1:string user, 2:i32 vm_id),

    string vm_migrate(1:string user, 2:i32 vm_id, 3:i32 host_id, 4:bool livemigration ),

    string get_vm_info(1:i32 vm_id),

    string get_vm_lcm_status(1:i32 vm_id),

    string vm_sub(1:string auth, 2:string CON_F),

    string vms_submit(1:string user, 2:string CON_F, 3:i32 num, 4:string os),

    string get_vm_ipv6(1:i32 vmid),

    string get_vm_ip(1:i32 id),

    string get_ip_list(1:string user, 2:string id_list), //id_list

    string get_image_detail(1:string user, 2:string image_name),
       
}
