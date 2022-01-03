import logging
import utils


def api(remote="http://localhost:8000"):
    class api:
        
        class mod:
            
            @staticmethod
            def fun(data: int, b: int, c: bool=None, d: int=None) -> int:
                """Example description
                multiline text
                
                Args:
                    data(int): TODO: description
                    b(int): TODO: description
                    c(bool): TODO: description
                    d(int): TODO: description
                
                Returns:
                    int
                """
                return utils.decode(utils.request(
                    method="POST",
                    url="%s/mod/fun/%s" % (remote, b),
                    params={"c": c, "d": d}, # requests does the to_string conversion
                    data=utils.encode(data)
                ))
    
    return api