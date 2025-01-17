import math

from pandas import DataFrame
from sklearn.grid_search import ParameterGrid

from __init__fuzzy import *


def experiment(sliding_number=3, hidden_nodes=15):
    print "New loop"
    dat_nn = np.asarray(scaler.fit_transform(dat))
    X_train_size = int(len(dat_nn) * 0.7)
    sliding = np.array(list(SlidingWindow(dat_nn, sliding_number)))
    X_train_nn = sliding[:X_train_size]
    y_train_nn = dat_nn[sliding_number:X_train_size + sliding_number].reshape(-1, 1)
    X_test_nn = sliding[X_train_size:]
    y_test_nn = dat_nn[X_train_size + sliding_number - 1:].reshape(-1, 1)
    y_actual_test = dat[X_train_size + sliding_number - 1:].tolist()

    fit_params = {
        'neural_shape': [len(X_train_nn[0]), hidden_nodes, 1]
    }
    ga_estimator = GAEstimator(cross_rate=0.5, mutation_rate=0.05, gen_size=100, pop_size=40)
    nn = NeuralFlowRegressor(hidden_nodes=[hidden_nodes], optimize='Adam'
                             , steps=7000, learning_rate=1E-03)
    classifier = OptimizerNNEstimator(ga_estimator, nn)
    classifier.fit(X_train_nn, y_train_nn, **fit_params)
    y_pred = scaler.inverse_transform(classifier.predict(X_test_nn))
    score_mape = mean_absolute_error(y_pred, y_actual_test)
    score_rmse = math.sqrt(mean_squared_error(y_pred, y_actual_test))
    np.savez('model_saved/GABPNN_%s_%s' % (sliding_number, score_mape), y_pred=y_pred, y_true=y_actual_test)
    return sliding_number, score_rmse, score_mape


sliding_number = np.arange(2, 6)
hidden_nodes = [15]
params = {
    "sliding_number": sliding_number,
    "hidden_nodes": hidden_nodes
}
param_grid = list(ParameterGrid(params))
result = [[experiment(sliding_number=param['sliding_number'], hidden_nodes=param['hidden_nodes']) for param in
          param_grid] for j in range(10)]
results = DataFrame(np.array(result).reshape(-1,3), columns=["sliding_number","rmse","mae"])
results.to_csv('experiment_logs/gabpnn_experiment.csv')
