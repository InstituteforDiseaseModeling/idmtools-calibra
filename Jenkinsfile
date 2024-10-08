podTemplate(
    //idleMinutes : 30,
    podRetention : onFailure(),
    activeDeadlineSeconds : 3600,
    containers: [
        containerTemplate(
            name: 'dtk-rpm-builder', 
            image: 'docker-production.packages.idmod.org/idm/dtk-rpm-builder:0.1',
            command: 'sleep', 
            args: '30d'
            )
  ]) {
  node(POD_LABEL) {
    container('dtk-rpm-builder'){
        def build_ok = true
		stage('Cleanup Workspace') {
			cleanWs()
			echo "Cleaned Up Workspace For Project"
			echo "${params.BRANCH}"
		}
		stage('Prepare') {
			sh 'python --version'
			sh 'python3 --version'
			sh 'pip3 --version'

			sh 'python3 -m pip install --upgrade pip'
			sh 'pip3 install wheel unittest-xml-reporting pytest'
			sh 'python3 -m pip install --upgrade setuptools'
			sh 'pip3 freeze'
			sh "pip3 install requests==2.29.0"
		}
		stage('Code Checkout') {
			if (env.CHANGE_ID) {
				echo "I execute on the pull request ${env.CHANGE_ID}"
				checkout([$class: 'GitSCM',
				branches: [[name: "pr/${env.CHANGE_ID}/head"]],
				doGenerateSubmoduleConfigurations: false,
				extensions: [],
				gitTool: 'Default',
				submoduleCfg: [],
				userRemoteConfigs: [[refspec: '+refs/pull/*:refs/remotes/origin/pr/*', credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2', url: 'git@github.com:InstituteforDiseaseModeling/idmtools_calibra.git']]])
			} else {
				echo "I execute on the ${env.BRANCH_NAME} branch"
				git branch: "${env.BRANCH_NAME}",
				credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2',
				url: 'git@github.com:InstituteforDiseaseModeling/idmtools_calibra.git'
            }
        }
		stage('Install, login') {
			def curDate = sh(returnStdout: true, script: "date").trim()
			echo "The current date is ${curDate}"

			if (params.idmtools_calibra_environment == 'Staging') {
				echo "I am installing idmtools_calibra from Staging"
				withCredentials([string(credentialsId: 'idm_bamboo_user', variable: 'user'), string(credentialsId: 'idm_bamboo_user_password', variable: 'password')]) {
					sh 'pip3 install idmtools_calibra --index-url=https://$user:$password@packages.idmod.org/api/pypi/pypi-staging/simple'
				}

			 } else if (params.idmtools_calibra_environment == 'Production'){
				 echo "I am installing idmtools_calibra from Production"
				 sh 'pip3 install idmtools_calibra --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'
			 } else {
				echo "I am installing idmtools_calibra from code"
				sh "pip3 install -r requirements.txt --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"
				sh "pip3 install idm-buildtools flake8 wheel matplotlib sqlalchemy black --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"
				//sh "python3 .dev_scripts/bootstrap.py"
				sh 'pip3 install -e .[test] --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'
				sh "pip3 install -r test_requirements.txt"
				sh "pip3 list"
			 }
			 sh 'pip3 install keyrings.alt'
			 sh "pip3 freeze"
			withCredentials([usernamePassword(credentialsId: 'comps_jenkins_user', usernameVariable: 'COMPS_USERNAME', passwordVariable: 'COMPS_PASSWORD'),
					         usernamePassword(credentialsId: 'comps2_jenkins_user', usernameVariable: 'COMPS2_USERNAME', passwordVariable: 'COMPS2_PASSWORD')])
			{
				sh 'python3 .dev_scripts/create_auth_token_args.py --comps_url https://comps2.idmod.org --username $COMPS2_USERNAME --password $COMPS2_PASSWORD'
				sh 'python3 .dev_scripts/create_auth_token_args.py --comps_url https://comps.idmod.org --username $COMPS_USERNAME --password $COMPS_PASSWORD'
			}
		}

		try{
			stage('Unit Test') {
				echo "Running Unit test Tests"
				dir('tests/unittests') {
					sh "pip3 install unittest-xml-reporting pytest "
					sh 'py.test -sv --junitxml=reports/test_results.xml'
					junit 'reports/*.xml'
				}
			}
		} catch(e) {
			build_ok = false
			echo e.toString()
		}

		try{
			stage('Integration Test') {
				echo "Running Integration Tests"
				dir('tests/integration') {
				    sh 'py.test -sv --junitxml=reports/test_results.xml'
				    junit 'reports/*.xml'
				}
			}
		} catch(e) {
			build_ok = false
			echo e.toString()
		}

		try{
			stage('Algorithms Test') {
				echo "Running algorithms Tests"
				dir('tests/algorithms') {
				    sh 'py.test -sv --junitxml=reports/test_results.xml'
				    junit 'reports/*.xml'
				}
			}
		} catch(e) {
			build_ok = false
			echo e.toString()
		}

        if(build_ok) {
    		currentBuild.result = "SUCCESS"
    	} else {
    		currentBuild.result = "FAILURE"
    	}
	}
 }
}
