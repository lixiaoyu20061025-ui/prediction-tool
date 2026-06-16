@@
 def register_blueprints(app):
@@
-    # Football blueprint (to be created)
+    # Football blueprint (to be created)
     try:
         from api.routes import create_football_blueprint
         app.register_blueprint(create_football_blueprint(), url_prefix='/api/football')
         logger.info('Football blueprint registered')
     except ImportError:
         logger.warning('Football blueprint not found')
@@
     except ImportError:
         logger.warning('Finance blueprint not found')
+    # Odds API for Sporttery scraper
+    try:
+        from football.api_odds import odds_bp
+        app.register_blueprint(odds_bp, url_prefix='/api/football')
+        logger.info('Football odds API registered')
+    except ImportError:
+        logger.warning('Football odds API not found')
