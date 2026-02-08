# Обзор источников

## Резюме

Обзор охватывает исследования в области предсказания исходов в ракетных видах спорта (теннис как ближайший аналог паделя), применения ML/DL для спортивной аналитики и методов анализа последовательностей игровых действий.

### Ключевые выводы

| Аспект | Выводы |
|--------|--------|
| **Базовые модели** | Логистическая регрессия, Elo-рейтинги, Bradley-Terry модели |
| **SOTA-модели** | XGBoost, LightGBM для табличных данных; LSTM/Transformer для последовательностей |
| **Метрики** | Accuracy, ROC-AUC, Log Loss, Brier Score для калибровки |
| **Feature Engineering** | Скользящие статистики, momentum-признаки, контекст счёта |
| **Данные** | Point-by-point статистика критична для локальных предсказаний |

---

## Источник 1: Forecasting the Winner of a Tennis Match

**Авторы:** Klaassen, F.J.G.M., Magnus, J.R.  
**Год:** 2003  
**Журнал:** Journal of the American Statistical Association, Vol. 98, No. 464  
**DOI:** https://doi.org/10.1198/016214503000000224

### Ключевые тезисы
- Классическая работа по вероятностному моделированию теннисных матчей
- Марковская модель для point-by-point предсказаний
- Введение концепции "важности очка" (point importance)

### Артефакты
- **Модель:** Марковская цепь с состояниями счёта
- **Ключевой признак:** Point importance = P(win match | win point) - P(win match | lose point)
- **Применение:** Расчёт вероятности победы в любой момент матча

### Применимость к работе
Концепция "важности очка" как признак для ML-моделей в паделе.

---

## Источник 2: Searching for the GOAT of tennis win prediction

**Авторы:** Kovalchik, S.A.  
**Год:** 2016  
**Журнал:** Journal of Quantitative Analysis in Sports, Vol. 12, Issue 3  
**DOI:** https://doi.org/10.1515/jqas-2015-0059

### Ключевые тезисы
- Систематическое сравнение методов предсказания в теннисе
- Анализ Elo, Glicko, Bradley-Terry моделей
- Важность калибровки вероятностей

### Артефакты
- **Лучшие модели:** Elo-based методы показывают ~70% accuracy
- **Метрика:** Log Loss для сравнения вероятностных предсказаний
- **Вывод:** Простые Elo-модели конкурентоспособны со сложными ML

### Применимость к работе
Baseline подход с Elo-рейтингами для сравнения с ML-моделями.

---

## Источник 3: XGBoost: A Scalable Tree Boosting System

**Авторы:** Chen, T., Guestrin, C.  
**Год:** 2016  
**Конференция:** KDD '16: Proceedings of the 22nd ACM SIGKDD  
**DOI:** https://doi.org/10.1145/2939672.2939785

### Ключевые тезисы
- Описание алгоритма XGBoost
- Регуляризация для предотвращения переобучения
- Эффективность на табличных данных

### Артефакты
- **Архитектура:** Gradient boosting с регуляризацией
- **Преимущества:** Скорость, интерпретируемость (feature importance)
- **Применение:** SOTA для табличных данных в соревнованиях Kaggle

### Применимость к работе
Основная модель для сравнения с baseline и DL-подходами.

---

## Источник 4: A survey of machine learning approaches for sports result prediction

**Авторы:** Bunker, R.P., Thabtah, F.  
**Год:** 2019  
**Журнал:** Applied Computing and Informatics  
**DOI:** https://doi.org/10.1016/j.aci.2017.09.005

### Ключевые тезисы
- Мета-обзор 50+ исследований по предсказанию спортивных результатов
- Сравнение ML-методов: логрегрессия, SVM, RF, нейросети
- Анализ признаков и метрик

### Артефакты
| Модель | Средняя Accuracy |
|--------|------------------|
| Logistic Regression | 62% |
| SVM | 64% |
| Random Forest | 66% |
| Neural Networks | 67% |

### Применимость к работе
Benchmark для оценки качества моделей, методология сравнения.

---

## Источник 5: Long Short-Term Memory

**Авторы:** Hochreiter, S., Schmidhuber, J.  
**Год:** 1997  
**Журнал:** Neural Computation, Vol. 9, Issue 8  
**DOI:** https://doi.org/10.1162/neco.1997.9.8.1735

### Ключевые тезисы
- Архитектура LSTM для обработки последовательностей
- Решение проблемы затухающего градиента
- Механизм gates для управления памятью

### Артефакты
- **Архитектура:** Input gate, forget gate, output gate
- **Применение:** Временные ряды, последовательности событий

### Применимость к работе
Базовая архитектура для моделирования последовательностей розыгрышей.

---

## Источник 6: Attention Is All You Need

**Авторы:** Vaswani, A., et al.  
**Год:** 2017  
**Конференция:** NeurIPS 2017  
**Ссылка:** https://arxiv.org/abs/1706.03762

### Ключевые тезисы
- Архитектура Transformer без рекуррентных связей
- Self-attention механизм
- Параллелизация вычислений

### Артефакты
- **Архитектура:** Multi-head attention, positional encoding
- **Преимущества:** Скорость обучения, качество на длинных последовательностях

### Применимость к работе
Альтернатива LSTM для моделирования последовательностей в паделе.

---

## Источник 7: Predicting the Outcome of Tennis Matches Using Machine Learning

**Авторы:** Sipko, M.  
**Год:** 2015  
**Источник:** Imperial College London, MEng Final Year Project  
**Ссылка:** https://www.doc.ic.ac.uk/teaching/distinguished-projects/2015/m.sipko.pdf

### Ключевые тезисы
- Сравнение ML-моделей для предсказания теннисных матчей
- Feature engineering на основе ATP статистики
- Анализ важности признаков

### Артефакты
- **Метрики:** Accuracy 65-70% на ATP данных
- **Лучшая модель:** Random Forest с Elo-признаками
- **Признаки:** Elo rating, surface-specific Elo, recent form

### Применимость к работе
Методология feature engineering применима к паделю.

---

## Источник 8: LightGBM: A Highly Efficient Gradient Boosting Decision Tree

**Авторы:** Ke, G., et al.  
**Год:** 2017  
**Конференция:** NeurIPS 2017  
**Ссылка:** https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree

### Ключевые тезисы
- Оптимизации для ускорения gradient boosting
- Histogram-based алгоритм
- Leaf-wise tree growth

### Артефакты
- **Скорость:** В 20+ раз быстрее XGBoost на некоторых датасетах
- **Качество:** Сопоставимо с XGBoost

### Применимость к работе
Альтернатива XGBoost для экспериментов.

---

## Источник 9: Elo rating system (Wikipedia + original paper)

**Автор:** Elo, A.E.  
**Год:** 1978  
**Книга:** The Rating of Chessplayers, Past and Present  
**Ссылка:** https://en.wikipedia.org/wiki/Elo_rating_system

### Ключевые тезисы
- Система рейтингования игроков на основе результатов матчей
- Формула ожидаемого результата
- Обновление рейтинга после матча

### Артефакты
- **Формула:** E = 1 / (1 + 10^((Rb - Ra) / 400))
- **K-фактор:** Скорость изменения рейтинга

### Применимость к работе
Baseline признак для всех моделей.

---

## Источник 10: Padel API Documentation

**Источник:** Official Padel API Documentation  
**Ссылка:** https://docs.padelapi.org/

### Доступные данные
| Уровень турнира | Score | Stats | Point-by-point |
|-----------------|-------|-------|----------------|
| Major | ✅ | ✅ | ✅ |
| P1 | ✅ | ✅ | ✅ |
| P2 | ✅ | ✅ | ✅ |
| FIP Platinum | ✅ | ✅ | ✅ |
| FIP Gold | ✅ | ❌ | ❌ |

### Применимость к работе
Основной источник данных для исследования.

---

## Рекомендуемые направления дополнительного поиска

1. **Google Scholar:** "tennis prediction machine learning", "sports outcome prediction"
2. **arXiv:** cs.LG (Machine Learning), stat.ML (Statistics ML)
3. **Papers with Code:** Sports Analytics tasks
4. **Kaggle:** Tennis datasets и notebooks

---

## Предлагаемый pipeline модели

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Raw Data      │────▶│ Feature Engineer │────▶│  ML Models      │
│  (Padel API)    │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌──────────────┐         ┌─────────────┐
                        │ Static       │         │ Baseline:   │
                        │ Features     │         │ LogReg, RF  │
                        │ - Elo        │         └─────────────┘
                        │ - H2H        │                │
                        │ - Form       │                ▼
                        └──────────────┘         ┌─────────────┐
                               │                 │ Advanced:   │
                               ▼                 │ XGBoost     │
                        ┌──────────────┐         └─────────────┘
                        │ Sequential   │                │
                        │ Features     │                ▼
                        │ - Rally seq  │         ┌─────────────┐
                        │ - Momentum   │         │ Deep:       │
                        └──────────────┘         │ LSTM/Trans  │
                                                 └─────────────┘
```

---

*Последнее обновление: Февраль 2026*
