# pyright: reportUnknownMemberType=false
# without it pylance type check will be crazy

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import cast
import logging

logger = logging.getLogger(__name__)

def create_average_month_temperature_graph(file_name : str) -> None:
    '''This function takes a xlsx file as input and plots a graph of the average temperature for each month.\n
    Save the graph as a png file in the results folder.
    Use show_graph() to show the graph.
    Args:
        file_name (str): The name of the file to be read
    Returns:
        None
    '''
    logger.info('Loading data...')
    data_path = os.path.join('data', f'{file_name}.xlsx')
    if not os.path.exists(data_path):
        logger.error(f'{data_path} not found')
        return
    df = pd.read_excel(data_path)
    logger.info('Data loaded, processing...')

    df['最高温度/℃'] = pd.to_numeric(df['最高温度/℃'], errors='coerce')
    df['最低温度/℃'] = pd.to_numeric(df['最低温度/℃'], errors='coerce')
    df.dropna(subset=['最高温度/℃', '最低温度/℃'], inplace=True)

    monthly_avg_temps = df.groupby('月')[['最高温度/℃', '最低温度/℃']].mean()
    monthly_avg_temps = cast(pd.DataFrame, monthly_avg_temps) # this is a dataframe but pylance doesn't think so
    monthly_avg_temps.rename(columns={
        '最高温度/℃': '平均最高温度',
        '最低温度/℃': '平均最低温度'
    }, inplace=True)
    logger.info('Data process complete')
    logger.debug(f'Result:\n\t{monthly_avg_temps}')

    logger.info('Plotting...')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(monthly_avg_temps.index, monthly_avg_temps['平均最高温度'], marker='o', linestyle='-', label='平均最高温度')
    ax.plot(monthly_avg_temps.index, monthly_avg_temps['平均最低温度'], marker='s', linestyle='--', label='平均最低温度')
    ax.set_title('月平均气温变化趋势图', fontsize=16)
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel('温度 (°C)', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'{i}月' for i in range(1, 13)])
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.tight_layout()
    os.makedirs('results', exist_ok=True)
    fig.savefig(os.path.join('results', '平均气温变化趋势图.png'))
    logger.info(f'Graph saved to {os.path.join('results', '平均气温变化趋势图.png')}')

def create_wind_speed_distribution_graph(file_name : str) -> None:
    '''This function takes a xlsx file as input and plots a graph of the wind speed distribution.\n
    Save the graph as a png file in the results folder.
    Use show_graph() to show the graph.
    Args:
        file_name (str): The name of the file to be read
    Returns:
        None
    '''
    logger.info('Loading data...')
    data_path = os.path.join('data', f'{file_name}.xlsx')
    if not os.path.exists(data_path):
        logger.error(f'{data_path} not found')
        return
    df = pd.read_excel(data_path)
    logger.info('Data loaded, processing...')

    def extract_wind_force(text : str) -> str | None:
        if ' ' in text:
            return text.split(' ')[-1]
        return None

    df['白天风力等级'] = df['白天风力风向'].apply(extract_wind_force)
    df['夜间风力等级'] = df['夜间风力风向'].apply(extract_wind_force)
    years_count = df['年'].nunique()

    day_slice = cast(pd.DataFrame, df[['月', '白天风力等级']]) # still this is a dataframe but pylance doesn't agree
    night_slice = cast(pd.DataFrame, df[['月', '夜间风力等级']])
    day_wind = day_slice.rename(columns={'白天风力等级': '风力等级'})
    night_wind = night_slice.rename(columns={'夜间风力等级': '风力等级'})
    all_wind_occurrences = pd.concat([day_wind, night_wind])
    all_wind_occurrences.dropna(subset=['风力等级'], inplace=True)
    wind_counts = all_wind_occurrences.groupby(['月', '风力等级']).size().reset_index(name='出现次数')
    wind_counts['年均出现次数'] = wind_counts['出现次数'] / years_count

    def get_wind_sort_key(level_string : str) -> int:
        match1 = level_string[0]
        match2 = ''
        if len(level_string) > 2:
            match2 = level_string[2]
        if match1.isdigit() and match2.isdigit():
            return int(match1) * 10 + int(match2)
        if match1.isdigit() and not match2.isdigit():
            return int(match1) * 10
        return 99

    unique_wind_levels = cast(np.ndarray[np.str_], wind_counts['风力等级'].unique()) # once again, pylance has its own opinion
    sorted_wind_levels = sorted(unique_wind_levels, key=get_wind_sort_key)
    logger.info('Data process complete')
    logger.debug(f'Result:\n\t{wind_counts}')

    logger.info('Plotting...')
    plt.rcParams['font.sans-serif'] = ['SimHei']

    plt.figure(figsize=(12, 8))

    sns.barplot(
        data=wind_counts,
        x='月',
        y='年均出现次数',
        hue='风力等级',
        palette='viridis',
        hue_order=sorted_wind_levels
    )

    plt.title('各月风力等级分布情况图', fontsize=20, pad=20)
    plt.xlabel('月份', fontsize=14)
    plt.ylabel('年均出现次数', fontsize=14)
    plt.xticks(ticks=range(0, 12), labels=[f'{i+1}月' for i in range(12)], fontsize=12)
    plt.legend(title='风力等级', fontsize=11, title_fontsize=13, bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout(rect=[0, 0, 0.95, 1])
    os.makedirs('results', exist_ok=True)
    plt.savefig(os.path.join('results', '风力等级分布情况图.png'))
    logger.info(f'Graph saved to {os.path.join('results', '风力等级分布情况图.png')}')

def create_weather_status_distribution_graph(file_name : str) -> None:
    '''This function takes a xlsx file as input and plots a graph showing the distribution of weather status in each month.\n
    Save the graph as a png file in the results folder.
    Use show_graph() to show the graph.
    Args:
        file_name (str): The name of the file to be read
    Returns:
        None
    '''
    logger.info('Loading data...')
    data_path = os.path.join('data', f'{file_name}.xlsx')
    if not os.path.exists(data_path):
        logger.error(f'{data_path} not found')
        return
    df = pd.read_excel(data_path)
    logger.info('Data loaded, processing...')

    day_slice = cast(pd.DataFrame, df[['月', '白天天气']]) # oh pylance what's wrong with you
    night_slice = cast(pd.DataFrame, df[['月', '夜间天气']])
    day_weather = day_slice.rename(columns={'白天天气': '天气'})
    night_weather = night_slice.rename(columns={'夜间天气': '天气'})
    weather = pd.concat([day_weather, night_weather])
    weather.dropna(subset=['天气'], inplace=True)
    weather_counts = weather.groupby(['月', '天气']).size().reset_index(name='出现次数')
    years_count = df['年'].nunique()
    weather_counts['年均出现次数'] = weather_counts['出现次数'] / years_count

    weather_order = [
        '晴', '多云', '阴',
        '小雨', '小到中雨', '中雨', '中到大雨', '大雨', '大到暴雨', '大暴雨',
        '阵雨', '雷阵雨',
        '雨夹雪', '阵雪', '小雪', '小到中雪', '中雪', '中到大雪', '大雪', '大到暴雪', '暴雪'
    ]
    weather_list = cast(np.ndarray[np.str_], weather_counts['天气'].unique()) # fix pylance type check asap please
    existing_weathers = list(weather_list)
    sorted_weather = [w for w in weather_order if w in existing_weathers]
    remaining_weather = [w for w in existing_weathers if w not in weather_order]
    sorted_weather += sorted(remaining_weather)
    logger.info('Data process complete')
    logger.debug(f'Result:\n\t{weather_counts}')

    logger.info('Plotting...')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.figure(figsize=(14, 8))

    sns.barplot(
        data=weather_counts,
        x='月',
        y='年均出现次数',
        hue='天气',
        hue_order=sorted_weather,
        palette='viridis'
    )

    plt.title('各月天气状况分布图', fontsize=20, pad=20)
    plt.xlabel('月份', fontsize=14)
    plt.ylabel('年均出现次数', fontsize=14)
    plt.xticks(ticks=range(0, 12), labels=[f'{i+1}月' for i in range(12)], fontsize=12)
    plt.legend(title='天气', title_fontsize=11, fontsize=13, bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout(rect=[0, 0, 0.95, 1])
    os.makedirs('results', exist_ok=True)
    plt.savefig(os.path.join('results', '天气状况分布图.png'))
    logger.info(f'Graph saved to {os.path.join('results', '天气状况分布图.png')}')

def show_graph():
    '''just a wrapper for plt.show()
    '''
    logger.info('Showing graph...')
    plt.show()
    logger.info('Showing done.')