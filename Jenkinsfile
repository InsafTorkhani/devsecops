pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'ls -la'
      }
    }

    stage('Secret scan (Gitleaks)') {
      steps {
        sh '''
          mkdir -p tools
          curl -sL https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz | tar -xz -C tools gitleaks
          ./tools/gitleaks detect --source . --no-git --exit-code 1 --report-path gitleaks-report.json
        '''
      }
    }

    stage('Dependency and config scan (Trivy)') {
      steps {
        sh '''
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ./tools
          ./tools/trivy fs --exit-code 1 --severity HIGH,CRITICAL .
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh 'docker build -t vulnerable-app:${BUILD_NUMBER} .'
      }
    }

    stage('SAST (Bandit)') {
      steps {
        sh '''
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -f json" > bandit-report.json || true
          docker run --rm vulnerable-app:${BUILD_NUMBER} sh -c "pip install -q bandit >/dev/null 2>&1 && bandit -r /app/app.py -lll"
        '''
      }
    }

    stage('Docker image scan (Trivy)') {
      steps {
        sh '''
          ./tools/trivy image --ignore-unfixed --exit-code 1 --severity HIGH,CRITICAL vulnerable-app:${BUILD_NUMBER}
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'gitleaks-report.json, bandit-report.json', allowEmptyArchive: true
    }
  }
}