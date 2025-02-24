import yaml
from collections import defaultdict
import os
import glob

def parse_yaml_content(content):
    try:
        return list(yaml.safe_load_all(content))
    except yaml.YAMLError as e:
        print(f"Error parsing YAML content: {str(e)}")
        return []

def parse_ingress_files():
    namespaces = defaultdict(list)
    files_processed = 0
    ingresses_found = 0
    
    # Recursively get all yaml files in all directories
    yaml_files = glob.glob('**/*.yaml', recursive=True)
    yaml_files.extend(glob.glob('**/*.yml', recursive=True))
    
    print(f"Found {len(yaml_files)} YAML files")
    
    for filepath in yaml_files:
        print(f"\nProcessing file: {filepath}")
        files_processed += 1
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                docs = parse_yaml_content(content)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    kind = doc.get('kind')
                    print(f"Found document of kind: {kind}")
                    
                    if isinstance(doc, dict) and doc.get('kind') == 'List':
                        # Handle List type documents
                        items = doc.get('items', [])
                        for item in items:
                            if item.get('kind') == 'Ingress':
                                ingresses_found += 1
                                process_ingress(item, namespaces)
                    elif isinstance(doc, dict) and doc.get('kind') == 'Ingress':
                        ingresses_found += 1
                        process_ingress(doc, namespaces)
                        
        except Exception as e:
            print(f"Error processing file {filepath}: {str(e)}")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Ingress resources found: {ingresses_found}")
    print(f"Namespaces found: {len(namespaces)}")
    
    return namespaces

def process_ingress(ingress, namespaces):
    namespace = ingress['metadata']['namespace']
    name = ingress['metadata']['name']
    
    # Extract host and service info
    hosts = []
    services = []
    for rule in ingress['spec'].get('rules', []):
        if 'host' in rule:
            hosts.append(rule['host'])
            for path in rule.get('http', {}).get('paths', []):
                if 'service' in path.get('backend', {}):
                    services.append(path['backend']['service']['name'])
    
    # Get annotations
    annotations = ingress['metadata'].get('annotations', {})
    alb_group = annotations.get('alb.ingress.kubernetes.io/group.name', 'default')
    scheme = annotations.get('alb.ingress.kubernetes.io/scheme', 'external')
    
    namespaces[namespace].append({
        'name': name,
        'hosts': hosts,
        'services': services,
        'alb_group': alb_group,
        'type': 'internal' if 'internal' in scheme else 'external'
    })

def generate_markdown(namespaces):
    markdown = "# Kubernetes Cluster Summary\n\n"
    
    for namespace, ingresses in sorted(namespaces.items()):
        markdown += f"## Namespace: {namespace}\n\n"
        
        # Add namespace description if available
        if namespace == "pro":
            markdown += "Production environment namespace\n\n"
        elif namespace == "dev":
            markdown += "Development environment namespace\n\n"
        elif namespace == "qa":
            markdown += "Quality Assurance environment namespace\n\n"
        
        markdown += "### Ingress Resources\n\n"
        markdown += "| Name | Type | ALB Group | Hosts | Backend Services |\n"
        markdown += "|------|------|-----------|-------|------------------|\n"
        
        for ingress in sorted(ingresses, key=lambda x: x['name']):
            hosts = "<br>".join(ingress['hosts'])
            services = "<br>".join(ingress['services'])
            markdown += f"| {ingress['name']} | {ingress['type']} | {ingress['alb_group']} | {hosts} | {services} |\n"
        
        markdown += "\n"
    
    return markdown

def main():
    current_dir = os.getcwd()
    print(f"Scanning directory: {current_dir}")
    print("Looking for YAML files in all subdirectories...\n")
    
    namespaces = parse_ingress_files()
    if not namespaces:
        print("No Ingress resources found in YAML files")
        return
    
    markdown = generate_markdown(namespaces)
    
    output_file = 'cluster_summary.md'
    with open(output_file, 'w') as f:
        f.write(markdown)
    print(f"\nSummary written to {output_file}")

if __name__ == "__main__":
    main()