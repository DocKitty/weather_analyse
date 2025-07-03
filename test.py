import os
import fetch
import analyse
import train

history = "dalian_weather_history"
now = "dalian_weather_now"

if not os.path.exists(os.path.join("data", history + ".xlsx")):
    fetch.fetch_weather_data_year(history, "dalian", "2022")
    fetch.fetch_weather_data_year(history, "dalian", "2023")
    fetch.fetch_weather_data_year(history, "dalian", "2024")
if not os.path.exists(os.path.join("data", now + ".xlsx")):
    for i in range(1, 7):
        fetch.fetch_weather_data(now, "dalian", "2025", str(i))
analyse.create_average_month_temperature_graph(history)
analyse.create_wind_speed_distribution_graph(history)
analyse.create_weather_status_distribution_graph(history)
model = train.train_model(history)
if model:
    train.predict(model, list(range(1, 13)), now)
train.show_graph()