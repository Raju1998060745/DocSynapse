from datetime import datetime, timezone

def compare_last_modified(previous_files, present_files):
    comparison_results = [] 
    try:
        
        previous_files_dict = {file['key']: file['last_modified'] for file in previous_files}
        
        
        for present_file in present_files:
            key = present_file['key']
            current_modified = present_file['last_modified']
            
            result = {
                'key': key,
                'size': present_file['size'],
                'last_modified': current_modified,
                'is_modified': True   # Default set to True for new files
            }
            
            #if file previously existed 
            if key in previous_files_dict:
                previous_modified = previous_files_dict[key]
                result['is_modified'] = current_modified > previous_modified
            
            comparison_results.append(result)
            
            
        return comparison_results
    
    except Exception as e:
        print(f"Error comparing files: {str(e)}")
        return []