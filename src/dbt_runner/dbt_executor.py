import os
import subprocess
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class DBTExecutor:
    def __init__(self):
        self.project_dir = os.getenv('DBT_PROFILES_DIR', '/app/dbt')
        self.profiles_dir = os.getenv('DBT_PROFILES_DIR', '/app/dbt')
        self.database_url = os.getenv('DATABASE_URL')
        
    def run_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a dbt command and return results"""
        try:
            env = os.environ.copy()
            env['DBT_PROFILES_DIR'] = self.profiles_dir
            
            result = subprocess.run(
                command,
                cwd=self.project_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out after 5 minutes',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def debug(self) -> Dict[str, Any]:
        """Run dbt debug to check configuration"""
        command = ['dbt', 'debug']
        return self.run_command(command)
    
    def deps(self) -> Dict[str, Any]:
        """Install dbt dependencies"""
        command = ['dbt', 'deps']
        return self.run_command(command)
    
    def run(self, models: List[str] = None, select: str = None) -> Dict[str, Any]:
        """Run dbt models"""
        command = ['dbt', 'run']
        
        if models:
            command.extend(['--models'] + models)
        elif select:
            command.extend(['--select', select])
            
        return self.run_command(command)
    
    def test(self, models: List[str] = None) -> Dict[str, Any]:
        """Run dbt tests"""
        command = ['dbt', 'test']
        
        if models:
            command.extend(['--models'] + models)
            
        return self.run_command(command)
    
    def seed(self) -> Dict[str, Any]:
        """Run dbt seed to load CSV files"""
        command = ['dbt', 'seed']
        return self.run_command(command)
    
    def snapshot(self) -> Dict[str, Any]:
        """Run dbt snapshots"""
        command = ['dbt', 'snapshot']
        return self.run_command(command)
    
    def generate_docs(self) -> Dict[str, Any]:
        """Generate dbt documentation"""
        command = ['dbt', 'docs', 'generate']
        return self.run_command(command)
    
    def serve_docs(self) -> Dict[str, Any]:
        """Serve dbt documentation"""
        command = ['dbt', 'docs', 'serve', '--port', '8080']
        return self.run_command(command)
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run complete dbt pipeline"""
        results = {}
        
        # Debug first
        debug_result = self.debug()
        results['debug'] = debug_result
        
        if not debug_result['success']:
            return results
        
        # Install dependencies
        deps_result = self.deps()
        results['deps'] = deps_result
        
        # Run models
        run_result = self.run()
        results['run'] = run_result
        
        # Run tests
        test_result = self.test()
        results['test'] = test_result
        
        # Generate docs
        docs_result = self.generate_docs()
        results['docs'] = docs_result
        
        return results
    
    def get_run_results(self) -> List[Dict[str, Any]]:
        """Get results from the latest dbt run"""
        try:
            results_file = os.path.join(self.project_dir, 'target', 'run_results.json')
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading run results: {e}")
            
        return []

def main():
    """Test function for dbt executor"""
    executor = DBTExecutor()
    
    # Test debug
    debug_result = executor.debug()
    print(f"Debug result: {debug_result['success']}")
    
    if debug_result['success']:
        # Test deps
        deps_result = executor.deps()
        print(f"Deps result: {deps_result['success']}")
        
        # Test run
        run_result = executor.run()
        print(f"Run result: {run_result['success']}")

if __name__ == "__main__":
    main() 