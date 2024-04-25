
class FilterSettingController:

    def __init__(self):
        self.load_filter()
        self.test = []

    def add_filter(self, filter_name: str):
        """Filter 추가 메서드"""
        pass
        
    def get_filter(self, filter_name):
        """Filter를 가져오게 하기"""
        return []
    
    def update_filter(self, filter_target_name: str, filter_name: str, face_filter_on: bool, updated_face_filter: list, updated_object_filter: list):
        """Filter 업데이트 메서드"""
        pass

    def delete_filter(self, filter_name: str):
        """Filter 삭제 메서드"""
        pass

    def get_filters(self):
        """Filter """
        return []
    
    def save_filter(self):
        """필터를 로컬에 저장합니다"""
        pass

    def load_filter(self):
        """필터를 로컬에서 가져옵니다."""
        pass
