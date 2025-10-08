import csv
import time
from typing import List, Tuple
from core.ollama.client import _make_ollama_request, test_ollama_connection
from core.config import OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL, OLLAMA_BACKUP_MODEL

def load_test_dataset(filename: str = 'spam_filter_dataset2.csv', limit: int = 50) -> List[Tuple[str, int]]:
    """Загружает тестовый датасет."""
    dataset = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            dataset.append((row['text'], int(row['label'])))
    return dataset

def test_model(model_name: str, dataset: List[Tuple[str, int]]) -> dict:
    """Тестирует модель на датасете."""
    print(f"\n🧪 Тестирование модели: {model_name}")
    print("=" * 50)
    
    correct = 0
    total = 0
    errors = 0
    true_positives = 0  # Правильно определенные угрозы
    false_positives = 0  # Ложные срабатывания
    true_negatives = 0   # Правильно определенные безопасные
    false_negatives = 0  # Пропущенные угрозы
    
    start_time = time.time()
    
    for text, true_label in dataset:
        total += 1
        prediction = _make_ollama_request(text, model_name)
        
        if prediction is None:
            errors += 1
            prediction = 0  # Считаем ошибки как безопасные
        
        # Подсчет метрик
        if prediction == true_label:
            correct += 1
            if true_label == 1:
                true_positives += 1
            else:
                true_negatives += 1
        else:
            if prediction == 1 and true_label == 0:
                false_positives += 1
            elif prediction == 0 and true_label == 1:
                false_negatives += 1
        
        # Показываем прогресс каждые 10 записей
        if total % 10 == 0:
            print(f"Обработано: {total}/{len(dataset)} | Точность: {correct/total:.1%}")
    
    end_time = time.time()
    
    # Вычисляем метрики
    accuracy = correct / total if total > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    result = {
        'model': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'total': total,
        'correct': correct,
        'errors': errors,
        'time': end_time - start_time,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives
    }
    
    return result

def print_results(results: dict):
    """Выводит результаты тестирования."""
    print(f"\n📊 РЕЗУЛЬТАТЫ для {results['model']}:")
    print(f"   Точность (Accuracy): {results['accuracy']:.1%}")
    print(f"   Полнота (Recall): {results['recall']:.1%}")
    print(f"   Точность (Precision): {results['precision']:.1%}")
    print(f"   F1-Score: {results['f1_score']:.3f}")
    print(f"   Время: {results['time']:.1f} сек")
    print(f"   Правильных: {results['correct']}/{results['total']}")
    print(f"   Ошибок: {results['errors']}")
    print()
    print(f"   Найдено угроз: {results['true_positives']}")
    print(f"   Пропущено угроз: {results['false_negatives']}")
    print(f"   Ложных срабатываний: {results['false_positives']}")
    print(f"   Правильно безопасных: {results['true_negatives']}")

def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестирования моделей Ollama")
    
    if not test_ollama_connection():
        print("❌ Ollama недоступна. Проверьте подключение.")
        return
    
    # Загружаем тестовый датасет (первые 50 записей для быстрого тестирования)
    print("📂 Загрузка тестового датасета...")
    dataset = load_test_dataset(limit=50)
    print(f"   Загружено: {len(dataset)} записей")
    
    safe_count = sum(1 for _, label in dataset if label == 0)
    threat_count = sum(1 for _, label in dataset if label == 1)
    print(f"   Безопасных: {safe_count}, Угроз: {threat_count}")
    
    # Список моделей для тестирования
    models = [OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL, OLLAMA_BACKUP_MODEL]
    all_results = []
    
    for model in models:
        try:
            result = test_model(model, dataset)
            print_results(result)
            all_results.append(result)
        except Exception as e:
            print(f"❌ Ошибка при тестировании {model}: {e}")
    
    # Сравнение моделей
    print("\n🏆 СРАВНЕНИЕ МОДЕЛЕЙ:")
    print("=" * 60)
    print(f"{'Модель':<30} {'Точность':<12} {'F1-Score':<12} {'Время':<10}")
    print("-" * 60)
    
    for result in all_results:
        model_short = result['model'].split(':')[0]
        print(f"{model_short:<30} {result['accuracy']:<11.1%} {result['f1_score']:<11.3f} {result['time']:<9.1f}s")

if __name__ == "__main__":
    main()