import processing
import time
import shutil   
import sys
import os
import argparse
import re

from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
                             QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QFileDialog, QHBoxLayout,QMessageBox,
                             QWidget)

from qgis.core import (QgsCoordinateReferenceSystem,QgsProject, 
                        QgsProviderRegistry, QgsProcessingAlgorithm,
                        QgsApplication, QgsProcessingContext, 
                        QgsProcessingFeedback, QgsRasterLayer,
                        QgsProcessingParameterRasterLayer, QgsProcessingParameterNumber,
                        QgsProcessingParameterCrs, QgsProcessingParameterExtent,
                        QgsProcessingParameterString, QgsProcessingParameterFeatureSink,
                        QgsProcessing, QgsProcessingMultiStepFeedback,
                        QgsExpression, QgsVectorLayer, 
                        QgsCoordinateTransform, QgsProcessingFeedback,
                        QgsProcessingFeatureSourceDefinition)
from qgis.gui import QgsProjectionSelectionWidget


QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
qgs = QgsApplication([], False)
qgs.initQgis()
from processing.core.Processing import Processing
