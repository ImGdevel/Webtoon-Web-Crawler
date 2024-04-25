from controllers.path_finder import *

class PersonFaceSettingController:

    def __init__(self):

        self.load_person_faces()
    
    def save_person_face(self):
        """현재까지 변경된 사항들을 파일에 저장"""
        pass

    def load_person_faces(self):
        """기존에 등록된 face정보를 로드함"""
        pass
    
    def add_person_face(self, new_face_name: str):
        """person_face 추가 메서드"""
        pass

    def add_person_encoding(self, face_name: str, file_path):
        """face_name과 file_path를 전달하면 face_name과 일치하는 객체에 배열을 추가"""
        return []
                
    def delete_person_face(self, person_name: str):
        """person_face 삭제 메서드"""
        pass

    def delete_person_encoding(self, person_name: str, encoding_name: str):
        """person_name의 encoding리스트 중 하나를 제거"""
        pass
        
    def get_person_face(self, person_name):
        """person_face를 가져오게 하기"""
        return []

    def get_person_encoding(self, person_name: str, encoding_name: str):
        """person_name이 가진 encoding_name에 해당하는 numpy배열을 반환"""
        return []
    
    def get_person_encodings(self, person_name: str):
        """한 사람의 모든 인코딩 리스트 반환"""
        return []

    def update_person_name(self, last_name:str, new_name:str):
        """last_name을 new_name으로 변경"""
        if False:
            return False
        
        return True

    def update_person_face(self, person_name, person: dict):
        """person_face 업데이트 메서드"""
        pass

    def get_person_faces(self):
        """person_face """
        return []
