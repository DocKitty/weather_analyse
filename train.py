# pyright: reportUnknownMemberType=false
# without it pylance type check will be crazy

import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sklearn.pipeline
import matplotlib.pyplot as plt
from typing import cast
import logging

logger = logging.getLogger(__name__)

def train_model(train_data_name: str) -> sklearn.pipeline.Pipeline | None:
    '''Train a model to predict the average monthly temperature using 8 degree polynomial regression.
    Args:
        train_data_name (str): The name of the training data file.
    Returns:
        sklearn.pipeline.Pipeline | None: The trained model.
    '''
    logger.info(f'Loading data from {train_data_name}.xlsx...')
    data_path = os.path.join('data', f'{train_data_name}.xlsx')
    if not os.path.exists(data_path):
        logger.error(f'{data_path} does not exist')
        return
    df = pd.read_excel(data_path)

    logger.info('Data loaded, preprocessing...')
    df['最高温度/℃'] = pd.to_numeric(df['最高温度/℃'], errors='coerce')
    df.dropna(subset=['年', '月', '最高温度/℃'], inplace=True)
    monthly_avg_temp = df.groupby('月')['最高温度/℃'].mean().reset_index()
    logger.info(f'Loaded {len(monthly_avg_temp)} data points')


    X_train = monthly_avg_temp[['月']]
    y_train = monthly_avg_temp['最高温度/℃']
    degree = 8
    model = sklearn.pipeline.make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X_train, y_train)
    logger.info('Model trained')

    return model

def predict(model : sklearn.pipeline.Pipeline, month: list[int], compare_data_name: str | None = None) -> None:
    '''Predict the average monthly temperature using the trained model and show the graph.\n
    Save the graph as a png file in the results folder.
    Use show_graph() to show the graph.
    Args:
        model (sklearn.pipeline.Pipeline): The trained model.
        month (list[int]): The month to predict, must be a continuous ascending sequence or one single month.
        compare_data_name (str, optional): The name of the data to compare with. Defaults to None.
    '''
    if (not month) or (sorted(month) != month) or (month[0] < 1) or (month[-1] > 12):
        logger.error('Invalid month')
        return
    
    logger.info('Looking for compare data')
    data_path = ''
    if compare_data_name == None:
        compare = False
        logger.info('No data to compare with, predict only')
    else:
        data_path = os.path.join('data', f'{compare_data_name}.xlsx')
        if not os.path.exists(data_path):
            compare = False
            logger.error(f'{data_path} does not exist, predict only')
        else:
            compare = True
            logger.info(f'Compare with {data_path}')
    
    logger.info('Predicting...')
    months_to_predict = pd.DataFrame({'月': month})
    predicted_temps = model.predict(months_to_predict)
    results_df = pd.DataFrame({
        '月': month,
        '预测平均最高温度': predicted_temps
        })
    logger.info(f'Predicted temperatures: {predicted_temps}')

    if compare:
        logger.info('Comparing...')
        compare_data_name = cast(str, compare_data_name) # pylance isn't smart enough
        df = pd.read_excel(data_path)
        df['最高温度/℃'] = pd.to_numeric(df['最高温度/℃'], errors='coerce')
        df.dropna(subset=['月', '最高温度/℃'], inplace=True)
        compare_temps = df.groupby('月')['最高温度/℃'].mean()
        compare_df = compare_temps.reset_index()
        compare_df.rename(columns={'最高温度/℃': '真实平均最高温度'}, inplace=True)
        logger.info(f'Compared with temperatures: {compare_df}')

        results_df = pd.merge(results_df, compare_df, on='月', how='left')
        logger.info(f'Comparison results: {results_df}')

    logger.info('Plotting...')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure()

    plt.plot(results_df['月'], results_df['预测平均最高温度'], marker='o', linestyle='--', label='预测平均最高温度')
    title = ''
    if compare:
        plt.plot(results_df['月'], results_df['真实平均最高温度'], marker='s', linestyle='-', label='真实平均最高温度')
        if len(month) == 1:
            title = f'2025年{month[0]}月平均最高温度：预测 vs 真实'
        else:
            title = f'2025年{month[0]}-{month[-1]}月平均最高温度：预测 vs 真实'
    else:
        if len(month) == 1:
            title = f'2025年{month[0]}月平均最高温度：预测'
        else:
            title = f'2025年{month[0]}-{month[-1]}月平均最高温度：预测'
    plt.title(title, fontsize=16)
    plt.xlabel('月份', fontsize=12)
    plt.ylabel('平均最高温度 / ℃', fontsize=12)
    plt.xticks(ticks=month, labels=[f'{m}月' for m in month])
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=12)
    os.makedirs('results', exist_ok=True)
    plt.savefig(os.path.join('results', f'{title}.png'))
    logger.info('Plotting done, saved as {title}.png')

def show_graph():
    '''just a wrapper for plt.show()
    '''
    logger.info('Showing graph...')
    plt.show()
    logger.info('Showing done')