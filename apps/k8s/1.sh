user=$(kubectl get serviceaccount -n kube-system | grep dashboard-username | wc -l)
auth=$(kubectl get clusterrolebinding | grep dashboard-username | wc -l)
if [ $user == 1 -a $auth == 1 ];then
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/dashboard-username/{print $1}') | grep "token:" | awk '{print $2}'
elif [ $user == 0 -a $auth == 1 ];then
kubectl create serviceaccount dashboard-username -n kube-system 2>&1 > /dev/null
kubectl delete clusterrolebinding dashboard-username 2>&1 > /dev/null
kubectl create clusterrolebinding dashboard-username --clusterrole=cluster-admin --serviceaccount=kube-system:dashboard-username 2>&1 > /dev/null
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/dashboard-username/{print $1}') | grep "token:" | awk '{print $2}'
elif [ $user == 1 -a $auth == 0 ];then
kubectl delete serviceaccount dashboard-username -n kube-system 2>&1 > /dev/null
kubectl create serviceaccount dashboard-username -n kube-system 2>&1 > /dev/null
kubectl create clusterrolebinding dashboard-username --clusterrole=cluster-admin --serviceaccount=kube-system:dashboard-username 2>&1 > /dev/null
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/dashboard-username/{print $1}') | grep "token:" | awk '{print $2}'
elif [ $user == 0 -a $auth == 0 ];then
kubectl create serviceaccount dashboard-username -n kube-system 2>&1 > /dev/null
kubectl create clusterrolebinding dashboard-username --clusterrole=cluster-admin --serviceaccount=kube-system:dashboard-username 2>&1 > /dev/null
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/dashboard-username/{print $1}') | grep "token:" | awk '{print $2}'
fi