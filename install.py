import os
import subprocess
import sys

def install_dependencies():
    # Install Docker (or any other dependencies your system needs)
    print("Installing Docker...")
    subprocess.run(["sudo", "apt-get", "install", "-y", "docker.io"], check=True)

    # Install Jenkins CLI or anything needed
    print("Installing Jenkins CLI...")
    subprocess.run(["curl", "-fsSL", "https://pkg.jenkins.io/debian/jenkins.io.key", "|", "sudo", "tee", "/etc/apt/trusted.gpg.d/jenkins.asc"], check=True)
    subprocess.run(["sudo", "sh", "-c", "'echo deb http://pkg.jenkins.io/debian/ /' > /etc/apt/sources.list.d/jenkins.list"], check=True)
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "jenkins"], check=True)

def configure_jenkins():
    print("Configuring Jenkins...")
    # Jenkins configuration, such as setting up credentials, installing plugins, etc.
    # Example for Jenkins plugin installation:
    subprocess.run(["java", "-jar", "/usr/share/jenkins/jenkins.war", "--httpPort=8080"], check=True)

def setup_cast_pipeline():
    # Copy the Jenkinsfile to the appropriate directory or configure your pipeline programmatically
    print("Setting up CAST pipeline...")
    with open('Jenkinsfile', 'w') as f:
        f.write("""
            pipeline {
                agent any
                stages {
                    stage('Clone') {
                        steps {
                            git branch: 'main', url: 'https://github.com/Kavyvachhani-fxis/Jenkins-Automation-BlogApp.git'
                        }
                    }
                    stage('Build') {
                        steps {
                            sh 'npm install'
                        }
                    }
                    stage('SonarQube Analysis') {
                        steps {
                            sh 'sonar-scanner'
                        }
                    }
                }
            }
        """)
    print("CAST pipeline configured.")

def main():
    print("Installing CAST Tool...")
    install_dependencies()
    configure_jenkins()
    setup_cast_pipeline()
    print("CAST Tool installation complete.")

if __name__ == "__main__":
    main()
