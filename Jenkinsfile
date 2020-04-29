pipeline {
    agent any

    triggers {
        pollSCM('H 21 * * *')
    }

    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
      PATH="/var/lib/jenkins/miniconda3/bin:$PATH"
    }

    stages {

        stage ("Code pull"){
            steps{
                checkout scm
            }
        }

        stage('Env py27') {
            steps {
                echo "Building py27 virtualenv"
                sh  ''' conda create --yes -n "${BUILD_TAG}py27" python=2.7
                    '''
            }
        }
        stage('Build savu-py27') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                sh  ''' source activate "${BUILD_TAG}py27"
                        conda config --set anaconda_upload no
                        cd install/savu_lite27/
                        conda build .
                    '''
            }
        }

        /*
        stage('Tests py35') {
            steps {
                sh  ''' source activate "${BUILD_TAG}py35"
                        conda install pytest pytest-cov
                        pytest -v --cov tests/
                    '''
            }
        }

        stage("Deploy py35") {
             steps {
                 sh ''' source activate "${BUILD_TAG}py35"
                        conda config --set anaconda_upload yes
                        source /var/lib/jenkins/upload.sh
                        anaconda -t $CONDA_UPLOAD_TOKEN upload -u dkazanc /var/lib/jenkins/.conda/envs/"${BUILD_TAG}py35"/conda-bld/linux-64/*.tar.bz2 --force
                    '''
             }
        }
    }

    post {
        always {
            sh ''' conda remove --yes -n "${BUILD_TAG}py27" --all
               '''
        }
        failure {
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']])
        }
    }

}
