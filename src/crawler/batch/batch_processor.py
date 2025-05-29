from typing import List, Callable, Tuple, Generator
from utils.logger import logger

class BatchProcessor:
    """배치 처리를 담당하는 클래스"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size

    def process_in_batches(
        self, 
        items: List[str], 
        process_func: Callable
    ) -> Generator[Tuple[List[dict], List[dict]], None, None]:
        """아이템들을 배치 단위로 처리하고 각 배치의 결과를 순차적으로 yield
        
        Args:
            items: 처리할 아이템 리스트
            process_func: 배치 처리 함수
        """
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min((batch_num + 1) * self.batch_size, len(items))
            current_batch = items[start_idx:end_idx]

            logger.info("배치 처리 중", extra={
                "batch_number": batch_num + 1,
                "total_batches": total_batches,
                "start_index": start_idx + 1,
                "end_index": end_idx
            })
            
            success_batch, failure_batch = process_func(current_batch)
            logger.info("배치 처리 완료", extra={
                "batch_number": batch_num + 1,
                "success_count": len(success_batch),
                "failure_count": len(failure_batch)
            })
            
            yield success_batch, failure_batch 